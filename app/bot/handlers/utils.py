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
)
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.utils.chatgpt import translate_promt2
from core.generation.photo import (
    learn_model_api, 
    wait_for_training, 
    generate_images, 
    wait_for_generation,
)
from core.generation.video import generate_video_from_image
from core.generation.utils import get_random_prompt
from loader import bot


BASE_DIR = Path(__file__).resolve().parent.parent


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
    print(imgs, gender)
    response = await learn_model_api(imgs, gender)
    tune_id = response.get("id")
    if not tune_id:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Служба поддержки",
            callback_data="support"
        )
        await messages[-1].answer(
            text="Произошла ошибка во время обучения модели. Пожалуйста, обратитесь в техническую поддержку", 
            reply_markup=builder.as_markup(),
        )
        return
    training_complete = await wait_for_training(tune_id)
    if training_complete:
        await create_tune(tune_id=str(tune_id), tg_user_id=str(messages[-1].chat.id), gender=gender)
        await update_user(tg_user_id=str(messages[0].chat.id), is_learn_model=False, tune_id=str(tune_id), gender=None)
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


async def save_promt(message: types.Message):
    promt = message.text
    for _ in range(5):
        try:
            promt = translate_promt2(promt)
            if promt:
                break
        except Exception as err:
            continue
    asyncio.create_task(
        update_user(str(message.chat.id), god_mod_text=promt)
    )
    
    
async def run_generation_photo_god_mod(
    call: types.CallbackQuery,
    user_db: dict,
    effect: str
):
    await call.message.answer("Создаем ваше фото, немного подождите")
    json_file = BASE_DIR / "media" / "promts.json"
    user_prompt = get_random_prompt(json_file=json_file, gender=user_db.get("gender"), category_slug=user_db.get("category"))
    await generate_photos_helper(
        tune_id=user_db.get('tune_id'),
        user_prompt=user_prompt,
        effect=effect,
        call=call
    )
    
    
async def generate_photos_helper(call: types.CallbackQuery, tune_id: str, user_prompt: str, effect: str):
    user_db = await get_user(str(call.message.chat.id))
    new_count_gen = user_db.get("count_generations") - 3
    asyncio.create_task(
        update_user(str(call.message.chat.id), count_generations=new_count_gen)
    )
    
    gen_response = await generate_images(
        tune_id=int(tune_id), 
        promt=user_prompt,
        effect=effect
    )
    if not gen_response or "id" not in gen_response:
        await call.message.answer("❌ Ошибка при запуске генерации изображений.", reply_markup=get_main_keyboard())
        new_count_gen = user_db.get("count_generations") + 3
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
        await call.message.answer("❌ Ошибка генерации изображения.")
    
    await bot.send_media_group(chat_id=call.message.chat.id, media=media_group.build())
    await delete_user_images(str(call.message.chat.id))


async def generate_video_from_photo_task(message: types.Message, photo_url: str, user_db: dict):
    
    
    try:
        new_count_gen = user_db.get("count_video_generations") - 1
        asyncio.create_task(
            update_user(str(message.chat.id), count_video_generations=new_count_gen)
        )
        video_url = await generate_video_from_image(photo_url)
        if not video_url:
            await message.answer("Произошла ошибка при генерации видео. Попробуйте еще раз. 😢")
            new_count_gen = user_db.get("count_video_generations") + 1
            asyncio.create_task(
                update_user(str(message.chat.id), count_video_generations=new_count_gen)
            )
            return
        
        await message.answer_video(video_url, caption=f"""Ваше видео готово! 🎥✨
                                   
<a href="https://t.me/photopingvin_bot?start">🖼 Создано в Пингвин ИИ</a>""")
        
        
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}. Попробуйте еще раз. 😢")


def get_main_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Стили"), types.KeyboardButton(text="Режим бога")],
            [types.KeyboardButton(text="Выбор аватара"), types.KeyboardButton(text="Генерации")],
            # [types.KeyboardButton(text="Оживление фото")],
            # [types.KeyboardButton(text="Доп. опции"), types.KeyboardButton(text="Служба поддержки")],
            [types.KeyboardButton(text="Служба поддержки")],
        ],
        resize_keyboard=True
    )
    
    