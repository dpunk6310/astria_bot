import os
import asyncio
from pathlib import Path

from aiogram import types

from core.backend.api import (
    get_user,
    create_tune,
    update_user,
    create_tg_image,
    get_random_prompt,
    get_price_list,
)
from core.logger.logger import get_logger
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.utils.chatgpt import translate_promt2, get_image_prompt
from core.generation.photo import (
    learn_model_api, 
    wait_for_training, 
    generate_images, 
    generate_images_from_image,
    wait_for_generation,
)
from core.generation.video import generate_video_from_image
from loader import bot


# BASE_DIR = Path(__file__).resolve().parent.parent
log = get_logger()

async def create_referal(user_db: dict, message: types.Message) -> dict:
    if not user_db.get("referal"):
        referal = message.text.split(" ")
        if len(referal) == 2:
            referal = referal[1]
            if referal != str(message.chat.id):
                await update_user(data={
                    "tg_user_id": str(message.chat.id),
                    "referal": referal,
                })

 
# async def download_user_images(m: types.Message):
#     photos_path = BASE_DIR / "media" / "photos"
    
#     if not os.path.exists(photos_path):
#         os.makedirs(photos_path)
        
#     if m.photo:
#         photo = await bot.get_file(m.photo[-1].file_id)
#         file_path = photo.file_path
#         output_filename = f"{photos_path}/{uuid4()}_{file_path.replace('photos/', '')}"
#         await m.bot.download_file(
#             file_path, destination=output_filename
#         )
#         await create_img_path(
#             tg_user_id=str(m.chat.id),
#             path=output_filename
#         )
#     if m.document:
#         photo = await m.bot.get_file(m.document.file_id)
#         file_path = photo.file_path
#         output_filename = f"{photos_path}/{uuid4()}_{file_path.replace('documents/', '')}"
#         await m.bot.download_file(
#             file_path, destination=output_filename
#         )
#         await create_img_path(
#             tg_user_id=str(m.chat.id),
#             path=output_filename
#         )
        
        
async def get_user_url_images(m: types.Message):
    if m.photo:
        photo = await bot.get_file(m.photo[-1].file_id)
        file_path = photo.file_path
        return f"https://api.telegram.org/file/bot{bot.token}/{file_path}"
    if m.document:
        photo = await m.bot.get_file(m.document.file_id)
        file_path = photo.file_path
        return f"https://api.telegram.org/file/bot{bot.token}/{file_path}"

        
async def process_learning(
    messages: list[types.Message],
    imgs_url: list[str],
    gender: str,
):
    response = await learn_model_api(imgs_url, gender)
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
        await update_user(data={
            "tg_user_id": str(messages[0].chat.id), 
            "is_learn_model": True
        })
        
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
        await update_user(data={
            "tg_user_id": str(messages[0].chat.id), 
            "is_learn_model": False, 
            "tune_id": str(tune_id), 
            "gender": gender
        })
        await messages[-1].answer(
            """Твой аватар создан ☑️
Теперь можно приступать к генерациям! Для этого нажми на кнопки "Стили" или "Режим бога" внизу экрана.
""", reply_markup=get_main_keyboard()
        )

    else:
        await messages[-1].answer(
            text="Произошла ошибка во время обучения модели. Пожалуйста, обратитесь в техническую поддержку. Код ошибки: 22", 
            reply_markup=builder.as_markup(),
        )
        log.error(f"Ошибка в обучении модели | UserID={messages[-1].chat.id} | Gender={gender} Код ошибки: 22")
        await update_user(data={
            "tg_user_id": str(messages[0].chat.id), 
            "is_learn_model": True
        })


async def save_promt(message: types.Message):
    promt = translate_promt2(message.text)
    await update_user(data={
        "tg_user_id": str(message.chat.id), 
        "god_mod_text": promt, 
    })
    

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
    
    
async def generate_photo_from_photo_helper(call: types.CallbackQuery, user_db: dict, image_url: str, effect: str):
    default_gen_count = 2
    default_deduct_count = default_gen_count * 2

    user_gen_count = user_db.get("count_generations", 0)

    if user_gen_count >= default_deduct_count:
        count_gen = default_gen_count
        deduct_gen = default_deduct_count
    else:
        count_gen = 1
        deduct_gen = 2

    if user_gen_count >= deduct_gen:
        new_count_gen = user_gen_count - deduct_gen
        asyncio.create_task(
            update_user(data={
                "tg_user_id": str(call.message.chat.id), 
                "count_generations": new_count_gen, 
            })
        )
    else:
        builder = InlineKeyboardBuilder()
        builder.button(
            text=f"Купить",
            callback_data=f"prices_photo"
        )
        await call.message.answer(f"У Вас недостаточно генераций: {user_db.get('count_generations', 0)} 😱", reply_markup=builder.as_markup())
        return
    
    await call.message.answer(f"""<b>Фото получено!</b> 👌

Начинаю обработку...
<b>Это займет примерно 55 секунд</b>""", parse_mode="HTML")
    user_prompt = get_image_prompt(image_url)
    if user_prompt == "":
        await call.message.answer("❌ Ошибка при запуске генерации изображений. Код ошибки 221.", reply_markup=get_main_keyboard())
        log.error(f"Ошибка при сохранение промпта | UserID={call.message.chat.id} | User promt:{user_prompt if user_prompt else 'пустой'} | Код ошибки: 221")
        new_count_gen = user_db.get("count_generations") + count_gen
        asyncio.create_task(
            update_user(data={
                "tg_user_id": str(call.message.chat.id), 
                "count_generations": new_count_gen, 
            })
        )
        return
    log.warning(effect)
    gen_response = await generate_images_from_image(
        tune_id=int(user_db.get("tune_id")), 
        prompt=f"sks {user_db.get('gender')} " + user_prompt,
        effect=effect,
        num_images=count_gen,
        image_url=image_url,
    )
    if not gen_response or "id" not in gen_response:
        await call.message.answer("❌ Ошибка при запуске генерации изображений. Код ошибки 21.", reply_markup=get_main_keyboard())
        log.error(f"Ошибка при запуске генерации изображений | UserID={call.message.chat.id} | User promt:{user_prompt} | Response = {gen_response} | Код ошибки: 21")
        new_count_gen = user_db.get("count_generations") + count_gen
        asyncio.create_task(
            update_user(data={
                "tg_user_id": str(call.message.chat.id), 
                "count_generations": new_count_gen, 
            })
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
        await call.message.answer("❌ Ошибка генерации изображения. Код ошибки: 211")
        log.error(f"Ошибка при запуске генерации изображений | UserID={call.message.chat.id} | not image urls(wait gen) | Код ошибки: 121")
        return
    
    messages = await bot.send_media_group(chat_id=call.message.chat.id, media=media_group.build())
    
    builder = InlineKeyboardBuilder()
    for i, message in enumerate(messages, 1):
        if message.photo:
            file_id = message.photo[-1].file_id
            img_response = await create_tg_image(str(call.message.chat.id), file_id)
            log.debug(img_response)
            
            builder.button(
                text=f"Фото {i}",
                callback_data=f"tovideo&&{img_response.get('id')}"
            )
    
    await call.message.answer(text="Превратить в видео 📹", reply_markup=builder.as_markup())
    
    
async def generate_photos_helper(call: types.CallbackQuery, tune_id: str, user_prompt: str, effect: str):
    user_db = await get_user(str(call.message.chat.id))
    count_gen = 3
    if 0 < user_db.get("count_generations", 0) < 3:
        count_gen = user_db.get("count_generations")
    new_count_gen = user_db.get("count_generations") - count_gen
    asyncio.create_task(
        update_user(data={
            "tg_user_id": str(call.message.chat.id), 
            "count_generations": new_count_gen, 
        })
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
            update_user(data={
                "tg_user_id": str(call.message.chat.id), 
                "count_generations": new_count_gen, 
            })
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
    
    builder = InlineKeyboardBuilder()
    for i, message in enumerate(messages, 1):
        if message.photo:
            file_id = message.photo[-1].file_id
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
            update_user(data={
                "tg_user_id": str(call.message.chat.id), 
                "count_video_generations": new_count_gen, 
            })
        )
        video_url = await generate_video_from_image(photo_url)
        if not video_url:
            await call.message.answer("Произошла ошибка при генерации видео. Попробуйте еще раз 😢. Код ошибки: 3")
            new_count_gen = user_db.get("count_video_generations") + 1
            asyncio.create_task(
                update_user(data={
                    "tg_user_id": str(call.message.chat.id), 
                    "count_video_generations": new_count_gen, 
                })
            )
            log.error(f"Произошла ошибка при генерации видео | UserID={call.message.chat.id} | Код ошибки: 3")
            return
        
        await call.message.answer_video(video_url, caption=f"""Ваше видео готово! 🎥✨
                                   
<a href="https://t.me/photopingvin_bot?start">🖼 Создано в Пингвин ИИ</a>""", parse_mode="HTML")

    except Exception as e:
        new_count_gen = user_db.get("count_video_generations") + 1
        asyncio.create_task(
            update_user(data={
                "tg_user_id": str(call.message.chat.id), 
                "count_video_generations": new_count_gen, 
            })
        )
        await call.message.answer("Произошла ошибка при генерации видео. Попробуйте еще раз 😢. Код ошибки: 33")
        log.error(f"Произошла ошибка при генерации видео | UserID={call.message.chat.id}| Error: {e} | Код ошибки: 33")


async def get_prices_photo(call: types.CallbackQuery):
    price_list = await get_price_list("photo")
    builder = InlineKeyboardBuilder()
    price_str = ""
    user_db = await get_user(str(call.message.chat.id))
    for i in price_list:
        if i.get("learn_model"):
            continue
        sale = i.get("sale", None)
        builder.button(
            text=f"{i.get('count')} фото",
            callback_data=f"inst_payment_{i.get('price')}_{i.get('count')}_{user_db.get('is_learn_model')}_0"
        )
        if not sale or sale == "":
            price_str += f"* {i.get('count')} фото: {i.get('price')}₽\n"
        else:
            price_str += f"* {i.get('count')} фото: {i.get('price')}₽ ({sale})\n"
    builder.adjust(2, 2, 2)
    await call.message.answer(
        text="""
Рады, что вам понравилось! 
Хотите больше генераций? 📸
Варианты:
{price_str}
Выберите свой вариант!

""".format(price_str=price_str),
        reply_markup=builder.as_markup()
    )


def get_main_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Стили"), types.KeyboardButton(text="Режим бога")],
            [types.KeyboardButton(text="Выбор аватара"), types.KeyboardButton(text="Фото по фото")],
            [types.KeyboardButton(text="Генерации"), types.KeyboardButton(text="Служба поддержки")],
            [types.KeyboardButton(text="Партнёрская программа"), types.KeyboardButton(text="FAQ")]
        ],
        resize_keyboard=True
    )
    
    # [types.KeyboardButton(text="Служба поддержки"), types.KeyboardButton(text="FAQ")],
            
    
    