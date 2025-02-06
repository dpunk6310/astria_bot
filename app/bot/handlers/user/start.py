from pathlib import Path
from uuid import uuid4
import os
from aiogram_media_group import media_group_handler


from aiogram import types, Router, F
from aiogram.filters import CommandStart
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger as log

from data.messages import use_messages
from core.backend.api import (
    create_user_db, 
    create_img_path, 
    delete_user_images, 
    get_user_images,
)
from core.generation.photo import (
    learn_model_api, 
    wait_for_training, 
    generate_images, 
    wait_for_generation
)
from loader import bot


user_router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class UploadImage(StatesGroup):
    photo = State()


@user_router.message(CommandStart())
@use_messages
async def start_handler(message: types.Message, messages):
    await create_user_db(
        tg_user_id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        username=message.from_user.username
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Инструкция",
            callback_data="inst"
        ),
        types.InlineKeyboardButton(
            text="Оплатить",
            callback_data="pay"
        ),
    )
    await message.answer(messages["start"], reply_markup=builder.as_markup())
    

@user_router.message(F.media_group_id)
@media_group_handler
async def handle_albums(messages: list[types.Message]):
    photos_path = BASE_DIR / "media" / "photos"
    
    if len(messages) != 10:
        await messages[-1].answer("Загрузить можно только 10 фото")
        return
        
    for m in messages:
        if m.photo:
            photo = await bot.get_file(m.photo[-1].file_id)
            output_filename = f"{photos_path}/{uuid4()}_{photo.file_path.replace('photos/', '')}"
            await m.bot.download_file(
                photo.file_path, destination=output_filename
            )
            response = await create_img_path(
                tg_user_id=str(m.chat.id),
                path=output_filename
            )
    
    await messages[-1].answer(
        """Мы получили твои фото и запустили разработку твоего персонального аватара, это займёт около 5 минут … 🔄

А ты пока обязательно подпишись на наш канал @…

Там мы публикуем оригинальные идеи стилей и промтов для твоих новых фотографий, а также актуальные новости.
""", 
    )
    images = await get_user_images(str(messages[-1].chat.id))
    imgs = []
    for i in images:
        imgs.append(i.get("path"))
    response = await learn_model_api(imgs)
    tune_id = response.get("id")
    training_complete = await wait_for_training(tune_id)
    if training_complete:
        keyboard = types.InlineKeyboardButton(
        keyboard=[
            [types.InlineKeyboardButton(text="Стили", callback_data="styles"), types.InlineKeyboardButton(text="Режим бога", callback_data="god_mod")],
            [types.InlineKeyboardButton(text="Аватар", callback_data="avatar"), types.InlineKeyboardButton(text="Генерации", callback_data="generation")],
            [types.InlineKeyboardButton(text="Настройки", callback_data="settings"), types.InlineKeyboardButton(text="Служба заботы", callback_data="service")],
        ],
        resize_keyboard=True
    )
        await messages[-1].answer(
            """Твой аватар создан ☑️
Теперь можно приступать к генерациям! Для этого нажми на кнопки "Стили" или "Режим бога" внизу экрана.
""", reply_markup=keyboard
        )


@user_router.callback_query(F.data == "inst")
async def inst_callback(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Дальше!",
            callback_data="upl_img_next"
        ),
    )
    await call.message.answer(
        text="Подойдут фотографии любого качества, но студийные могут дать лучший результат!",
        reply_markup=builder.as_markup()
    )
    
    
@user_router.callback_query(F.data == "upl_img_next")
async def upl_img_next_callback(call: types.CallbackQuery):
    await call.message.answer(
        text="""
        ИНСТРУКЦИЯ...

Загрузи 10 фото, чтобы обучить бота и получить доступ к генерации 📲

Важно:
    – Загружайте строго 10 фото. Не 5, не 8 и не 16.
    – Используй крупные планы своего лица или селфи, избегай снимков с дальнего расстояния.
    – На фото должен(на) быть только ты — без родителей, бабушек и домашних животных.
    – Не выбирайте фото с резкими эмоциями, максимум легкая улыбка.
    – Загружай фото в прямой позе, без наклонов головы или шеи.
    – Убедитесь в хорошем освещении фотографии для получения качественного результата.

Загрузить фото и обучить бота можно только один раз! Подходите внимательно к выбору фото и строго следуйте инструкции!

Если iPhone предложит «Конвертировать в JPEG», соглашайся 👍

Теперь просто отправь 10 фотографий в бота ⬇️

        """,
    )


# @user_router.callback_query(F.data == "learn_model")
# async def learn_model_callback(call: types.CallbackQuery):
#     images = await get_user_images(str(call.message.chat.id))
#     imgs = []
#     for i in images:
#         imgs.append(i.get("path"))
#     response = await learn_model_api(imgs)
#     tune_id = response.get("id")
#     # await call.message.answer(f"Модель обучается... Tune ID: {tune_id}")

#     training_complete = await wait_for_training(tune_id)

#     if training_complete:
#         builder = InlineKeyboardBuilder()
#         builder.add(
#             types.InlineKeyboardButton(
#                 text="Генерация",
#                 callback_data=f"generation_{tune_id}"
#             ),
#         )
#         await call.message.answer(
#             "✅ Обучение модели завершено! Начинаю генерировать изображения 🎨", 
#             reply_markup=builder.as_markup()
#         )
#     else:
#         await call.message.answer("❌ Обучение модели не удалось завершить. Попробуйте позже.")
    
    
@user_router.message(F.text == "Стили")
async def generation_callback(call: types.CallbackQuery):
    tune_id = call.data.split("_")[1]
    user_prompt = "a painting of sks man / woman in the style of Van Gogh"      
    gen_response = await generate_images(tune_id=tune_id, promt=user_prompt)
    
    if not gen_response or "id" not in gen_response:
        await call.message.answer("❌ Ошибка при запуске генерации изображений.")
        return

    prompt_id = gen_response["id"]
    await call.message.answer(f"🖼 Генерация изображения... Prompt ID: {prompt_id}")

    image_urls = await wait_for_generation(prompt_id)
    media_group = MediaGroupBuilder(caption="🖼 Ваши фото успешно сгенерированы")
    if image_urls:
        for i in image_urls:
            media_group.add(type="photo", media=i)

    else:
        await call.message.answer("❌ Ошибка генерации изображения.")
        
    await bot.send_media_group(chat_id=call.message.chat.id, media=media_group.build())
    
    await delete_user_images(str(call.message.chat.id))

    

