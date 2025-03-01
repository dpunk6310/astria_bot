import os
import asyncio
from pathlib import Path
from uuid import uuid4

from aiogram import types

from core.backend.api import (
    create_img_path, 
    delete_user_images, 
    get_user,
    create_tune,
    update_user,
    create_tg_image,
)
from core.logger.logger import get_logger
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.utils.chatgpt import translate_promt2
from core.generation.photo import (
    learn_model_api, 
    wait_for_training, 
    generate_images, 
    wait_for_generation,
)
from core.backend.api import get_random_prompt
from core.generation.video import generate_video_from_image
from loader import bot


BASE_DIR = Path(__file__).resolve().parent.parent
log = get_logger()

async def create_referal(user_db: dict, message: types.Message) -> dict:
    if not user_db.get("referal"):
        referal = message.text.split(" ")
        if len(referal) == 2:
            referal = referal[1]
            if referal != str(message.chat.id):
                await update_user(str(message.chat.id), referal=referal)

 
async def download_user_images(m: types.Message):
    photos_path = BASE_DIR / "media" / "photos"
    
    if not os.path.exists(photos_path):
        os.makedirs(photos_path)
        
    if m.photo:
        photo = await bot.get_file(m.photo[-1].file_id)
        file_path = photo.file_path
        output_filename = f"{photos_path}/{uuid4()}_{file_path.replace('photos/', '')}"
        await m.bot.download_file(
            file_path, destination=output_filename
        )
        await create_img_path(
            tg_user_id=str(m.chat.id),
            path=output_filename
        )
    if m.document:
        photo = await m.bot.get_file(m.document.file_id)
        file_path = photo.file_path
        output_filename = f"{photos_path}/{uuid4()}_{file_path.replace('documents/', '')}"
        await m.bot.download_file(
            file_path, destination=output_filename
        )
        await create_img_path(
            tg_user_id=str(m.chat.id),
            path=output_filename
        )
        
        
async def process_learning(
    messages: list[types.Message],
    imgs: list[str],
    gender: str,
):
    response = await learn_model_api(imgs, gender)
    tune_id = response.get("id")
    if not tune_id:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Служба поддержки",
            callback_data="support"
        )
        await messages[-1].answer(
            text="Произошла ошибка во время обучения модели. Пожалуйста, обратитесь в техническую поддержку. Код ошибки: 2", 
            reply_markup=builder.as_markup(),
        )
        log.error(f"Ошибка в обучении модели. UserID={messages[-1].chat.id} | Gender={gender} Код ошибки: 2")
        await update_user(tg_user_id=str(messages[0].chat.id), is_learn_model=True)
        return
    training_complete = await wait_for_training(tune_id)
    if training_complete:
        tune_db = await create_tune(tune_id=str(tune_id), tg_user_id=str(messages[-1].chat.id), gender=gender)
        if not tune_db:
            await messages[-1].answer(
                text="Произошла ошибка во время обучения модели. Пожалуйста, обратитесь в техническую поддержку. Код ошибки: 222", 
                reply_markup=builder.as_markup(),
            )
            log.error(f"Ошибка в обучении модели. UserID={messages[-1].chat.id} | Gender={gender} tune_db = {tune_db} Код ошибки: 2222")
            return
        await update_user(tg_user_id=str(messages[0].chat.id), is_learn_model=False, tune_id=str(tune_id), gender=gender)
        await messages[-1].answer(
            """Твой аватар создан ☑️
Теперь можно приступать к генерациям! Для этого нажми на кнопки "Стили" или "Режим бога" внизу экрана.
""", reply_markup=get_main_keyboard()
        )
        for i in imgs:
            try:
                os.remove(i)
            except Exception as err:
                continue
    else:
        await messages[-1].answer(
            text="Произошла ошибка во время обучения модели. Пожалуйста, обратитесь в техническую поддержку. Код ошибки: 22", 
            reply_markup=builder.as_markup(),
        )
        log.error(f"Ошибка в обучении модели | UserID={messages[-1].chat.id} | Gender={gender} Код ошибки: 22")
        await update_user(tg_user_id=str(messages[0].chat.id), is_learn_model=True)


async def save_promt(message: types.Message):
    promt = translate_promt2(message.text)
    upd_user = await update_user(str(message.chat.id), god_mod_text=promt)
    log.debug(f"update user promt = {upd_user}")
    
    

async def run_generation_photo(
    call: types.CallbackQuery,
    user_db: dict,
    effect: str
):
    await call.message.answer("Создаем ваше фото, немного подождите")
    user_prompt = await get_random_prompt(category_slug=user_db.get("category"))
    await generate_photos_helper(
        tune_id=user_db.get('tune_id'),
        user_prompt=user_prompt,
        effect=effect,
        call=call
    )
    
    
async def generate_photos_helper(call: types.CallbackQuery, tune_id: str, user_prompt: str, effect: str):
    user_db = await get_user(str(call.message.chat.id))
    count_gen = 3
    if user_db.get("count_generations") < 3:
        count_gen = user_db.get("count_generations")
    new_count_gen = user_db.get("count_generations") - count_gen
    asyncio.create_task(
        update_user(str(call.message.chat.id), count_generations=new_count_gen)
    )
    gen_response = await generate_images(
        tune_id=int(tune_id), 
        prompt=user_prompt,
        effect=effect,
        num_images=count_gen
    )
    if not gen_response or "id" not in gen_response:
        await call.message.answer("❌ Ошибка при запуске генерации изображений. Код ошибки 1.", reply_markup=get_main_keyboard())
        log.error(f"Ошибка при запуске генерации изображений | UserID={call.message.chat.id} | User promt:{user_prompt} | Response = {gen_response} | Код ошибки: 1")
        new_count_gen = user_db.get("count_generations") + count_gen
        asyncio.create_task(
            update_user(str(call.message.chat.id), count_generations=new_count_gen)
        )
        return

    user_db = await get_user(str(call.message.chat.id))
    prompt_id = gen_response.get("id")
    if user_db.get("count_generations") < 3:
        await call.message.answer("""
<b>У Вас осталось {count_gen} генераций!</b>

Получи эксклюзивный доступ к миру ИИ-фотографии!  🎁  

<b>Мы дарим дополнительные генерации в нашем боте!</b>

🎁 Как получить 10 бесплатных генераций:

1. Подпишись на наш Instagram: https://www.instagram.com/photopingvin.ai
2. Поделись своим волшебным ИИ-фото в Stories.
3. Отметь нас @photopingvin.ai и добавь кликабельную ссылку на бота: https://t.me/photopingvin_bot?start={user_tg_id}

🎁 <b>Хочешь 30 бесплатных генераций?</b>

1. Создай совместный пост (функция Соавторство) с нашим аккаунтом @photopingvin.ai
2. Поделись своими потрясающими ИИ-фотографиями и расскажи о своих впечатлениях!

<b>Отправь скриншот своей публикации в поддержку @managerpingvin_ai – и мы начислим бонусные генерации на твой аккаунт!  Ждём твои креативные работы!</b>

*Instagram принадлежит компании Meta, признанной экстремистской организацией и запрещенной в РФ""".format(
    count_gen=user_db.get("count_generations"), user_tg_id=str(call.message.chat.id)), parse_mode="HTML",
)

    image_urls = await wait_for_generation(prompt_id)
    media_group = MediaGroupBuilder(caption='<a href="https://t.me/photopingvin_bot?start">🖼 Создано в Пингвин ИИ</a>')
    
    if image_urls:
        for i in image_urls:
            media_group.add(type="photo", media=i, parse_mode="HTML")
    else:
        await call.message.answer("❌ Ошибка генерации изображения. Код ошибки: 11")
        log.error(f"Ошибка при запуске генерации изображений | UserID={call.message.chat.id} | not image urls(wait gen) | Код ошибки: 11")
        return
    
    messages = await bot.send_media_group(chat_id=call.message.chat.id, media=media_group.build())
    asyncio.create_task(delete_user_images(str(call.message.chat.id)))
    
    builder = InlineKeyboardBuilder()
    for i, message in enumerate(messages, 1):
        if message.photo:
            file_id = message.photo[-1].file_id
            log.debug(file_id)
            img_response = await create_tg_image(str(call.message.chat.id), file_id)
            log.debug(img_response)
            
            builder.button(
                text=f"Фото {i}",
                callback_data=f"tovideo&&{img_response.get('id')}"
            )
    
    await call.message.answer(text="Превратить в видео 📹", reply_markup=builder.as_markup())


async def generate_video_from_photo_task(call: types.CallbackQuery, photo_url: str, user_db: dict):
    try:
        new_count_gen = user_db.get("count_video_generations") - 1
        asyncio.create_task(
            update_user(str(call.message.chat.id), count_video_generations=new_count_gen)
        )
        video_url = await generate_video_from_image(photo_url)
        if not video_url:
            await call.message.answer("Произошла ошибка при генерации видео. Попробуйте еще раз 😢. Код ошибки: 3")
            new_count_gen = user_db.get("count_video_generations") + 1
            asyncio.create_task(
                update_user(str(call.message.chat.id), count_video_generations=new_count_gen)
            )
            log.error(f"Произошла ошибка при генерации видео | UserID={call.message.chat.id} | Код ошибки: 3")
            return
        
        await call.message.answer_video(video_url, caption=f"""Ваше видео готово! 🎥✨
                                   
<a href="https://t.me/photopingvin_bot?start">🖼 Создано в Пингвин ИИ</a>""", parse_mode="HTML")

    except Exception as e:
        new_count_gen = user_db.get("count_video_generations") + 1
        asyncio.create_task(
            update_user(str(call.message.chat.id), count_video_generations=new_count_gen)
        )
        await call.message.answer("Произошла ошибка при генерации видео. Попробуйте еще раз 😢. Код ошибки: 33")
        log.error(f"Произошла ошибка при генерации видео | UserID={call.message.chat.id}| Error: {e} | Код ошибки: 33")


def get_main_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Стили"), types.KeyboardButton(text="Режим бога")],
            [types.KeyboardButton(text="Выбор аватара"), types.KeyboardButton(text="Генерации")],
            [types.KeyboardButton(text="Служба поддержки"), types.KeyboardButton(text="FAQ")],
        ],
        resize_keyboard=True
    )
    
    