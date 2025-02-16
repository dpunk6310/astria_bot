import asyncio
from pathlib import Path

from aiogram import types, Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.backend.api import (
    get_user,
    update_user,
)

from .utils import (
    generate_video_from_photo_task
)


gen_video_router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent


@gen_video_router.message(F.text == "Оживление фото")
async def bring_photo_to_life(message: types.Message):
    user_db = await get_user(message.chat.id)
    await message.answer(
        text="""
<b>Спасибо что ты с нами, ты такой талантливый! А талантливым людям надо держаться вместе</b> 🖖🤝❤️

Загрузи 1 фотографию в хорошем качестве.

У тебя осталось оживлений фото: <b>{count_gen}</b>
""".format(count_gen=user_db.get("count_video_generations")),
        parse_mode="HTML"
    )
    
    
@gen_video_router.message(F.photo)
async def handle_photo_upload(message: types.Message):
    user_db = await get_user(message.chat.id)
    
    if user_db.get("count_video_generations", 0) <= 0:
        await message.answer("У вас закончились попытки для генерации видео. 😢")
        return
    
    photo = message.photo[-1]
    file_id = photo.file_id
    
    file = await message.bot.get_file(file_id)
    file_path = file.file_path
    photo_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file_path}"
    
    await message.answer("Фото получено! Начинаю обработку... 🛠️")
    
    asyncio.create_task(generate_video_from_photo_task(message, photo_url, user_db))



def setup(dp):
    dp.include_router(gen_video_router)
