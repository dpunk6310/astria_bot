from pathlib import Path
from typing import List
import os

from aiogram import types, Router
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.messages import use_messages
from core.backend.api import create_user_db
from loader import bot


user_router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent.parent


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
    
    photo_path = BASE_DIR / "media/logo_p.png"
    
    await message.answer_photo(
        photo=FSInputFile(photo_path),
        caption=messages["start"],
        reply_markup=builder.as_markup()
    )
    

@user_router.message()
async def handle_albums(message: types.Message):
    photos = message.photo
    if photos:
        if not os.path.exists(BASE_DIR / "media" / "photos"):
            os.makedirs(BASE_DIR / "media/photos/")
        photo = await bot.get_file(photos[-1].file_id)
        await message.bot.download_file(photo.file_path, destination=BASE_DIR / "media" / photo.file_path)
        await bot.send_photo(
            message.chat.id, FSInputFile(BASE_DIR / "media" / photo.file_path), caption="Вот оно"
        )
        # os.remove(photo.file_path)