import asyncio
from pathlib import Path

from aiogram import types, Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger as log

from core.backend.api import (
    get_user,
    update_user,
)
from .utils import (
    generate_video_from_photo_task
)
from loader import bot


gen_video_router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent


@gen_video_router.callback_query(F.data.contains("tovideo"))
async def bring_photo_to_life(call: types.CallbackQuery):
    file_path = call.data.split("&&")[1]
    log.debug(file_path)
    user_db = await get_user(str(call.message.chat.id))
    
    if user_db.get("count_video_generations", 0) <= 0:
        await call.message.answer("У вас закончились попытки для генерации видео. 😢")
        return
    
    
    photo_url = f"https://api.telegram.org/file/bot{bot.token}/{file_path}"
    log.debug(photo_url)
    await call.message.answer("Фото получено! Начинаю обработку... 🛠️")
    
    asyncio.create_task(generate_video_from_photo_task(call, photo_url, user_db))


def setup(dp):
    dp.include_router(gen_video_router)
