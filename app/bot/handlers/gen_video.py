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
    
    if user_db.get("count_video_generations") <= 0:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Купить",
            callback_data="prices_video"
        )
        await call.message.answer("У вас закончились попытки для генерации видео. 😢", reply_markup=builder.as_markup())
        return
    photo_url = f"https://api.telegram.org/file/bot{bot.token}/{file_path}"
    await call.message.answer("""<b>Фото получено!</b> 👌

Начинаю обработку...
<b>Это займет примерно 5 минут</b>""", parse_mode="HTML")
    
    asyncio.create_task(generate_video_from_photo_task(call, photo_url, user_db))


def setup(dp):
    dp.include_router(gen_video_router)
