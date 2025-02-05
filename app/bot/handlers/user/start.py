from pathlib import Path
from uuid import uuid4
import os

from aiogram import types, Router, F
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile
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
from core.generation.photo import learn_model_api, wait_for_training, generate_images, wait_for_generation
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
    builder.add(
        types.InlineKeyboardButton(
            text="Загрузить фото",
            callback_data="upload_images"
        ),
    )
    
    photo_path = BASE_DIR / "media/logo_p.png"
    await message.answer(messages["start"], reply_markup=builder.as_markup())
    # await message.answer_photo(
    #     photo=FSInputFile(photo_path),
    #     caption=messages["start"],
    #     reply_markup=builder.as_markup()
    # )
    

@user_router.message()
async def handle_albums(message: types.Message):
    photos_path = BASE_DIR / "media" / "photos"
    photos = message.photo
    if photos:
        
        # Добавить проверку баланса
        
        if not os.path.exists(photos_path):
            os.makedirs(photos_path)
            
        photo = await bot.get_file(photos[-1].file_id)
        photo_file = photo.file_path
        output_filename = f"{photos_path}/{uuid4()}_{photo_file.replace('photos/', '')}"
        
        await message.bot.download_file(
            photo_file, destination=output_filename
        )
        response = await create_img_path(
            tg_user_id=str(message.chat.id),
            path=output_filename
        )
        # log.debug(images)
        # await bot.send_photo(
        #     message.chat.id, FSInputFile(BASE_DIR / "media" / photo.file_path), caption="Вот оно"
        # )

@user_router.callback_query(F.data == "upload_images")
async def upload_images_callback(call: types.CallbackQuery):
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
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Обучение модели",
            callback_data="learn_model"
        ),
    )
    await call.message.answer(
        text="""
        ИНСТРУКЦИЯ

Загрузи 10 фото, чтобы обучить бота и получить доступ к генерации 📲

Важно:
    – Загружайте строго 10 фото. Не 5, не 8 и не 16.
    – Используй крупные планы своего лица или селфи, избегай снимков с дальнего расстояния.
    – На фото должен(на) быть только ты — без родителей, бабушек и домашних животных.
    – Не выбирайте фото с резкими эмоциями, максимум легкая улыбка.
    – Загружай фото в прямой позе, без наклонов головы или шеи.
    – Убедитесь в хорошем освещении фотографии для получения качественного результата.

Загрузить фото и обучить бота можно только один раз! Подходите внимательно к выбору фото и строго следуйте инструкции!

После загрузки нажми на кнопку "Обучение модели"
        """,
        reply_markup=builder.as_markup()
    )


@user_router.callback_query(F.data == "learn_model")
async def learn_model_callback(call: types.CallbackQuery):
    # await call.message.answer(
    #     text="Запустил обучение модели",
    # )
    # images = await get_user_images(str(call.message.chat.id))
    # imgs = []
    # for i in images:
    #     imgs.append(i.get("path"))
    # response = await learn_model_api(imgs)
    # tune_id = response.get("id")
    # await call.message.answer(f"Модель обучается... Tune ID: {tune_id}")

    # training_complete = await wait_for_training(tune_id)

    # if training_complete:
    #     await call.message.answer("✅ Обучение модели завершено! Начинаю генерировать изображения 🎨")
    # else:
    #     await call.message.answer("❌ Обучение модели не удалось завершить. Попробуйте позже.")
    
    user_prompt = "a painting of sks man / woman in the style of Van Gogh"      
    tune_id = 2104287
    gen_response = await generate_images(tune_id=tune_id, promt=user_prompt)
    
    if not gen_response or "id" not in gen_response:
        await call.message.answer("❌ Ошибка при запуске генерации изображений.")
        return

    prompt_id = gen_response["id"]
    await call.message.answer(f"🖼 Генерация изображения... Prompt ID: {prompt_id}")

    image_urls = await wait_for_generation(prompt_id)
    
    img_msg = ""
    for i in image_urls:
        img_msg += f"{i}\n"
    
    if image_urls:
        await call.message.answer(img_msg)
    else:
        await call.message.answer("❌ Ошибка генерации изображения.")
    
    await delete_user_images(str(call.message.chat.id))
    
    
        
    

    

