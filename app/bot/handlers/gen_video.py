import asyncio
from pathlib import Path

from aiogram import types, Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from core.generation.video import generate_video
from core.backend.api import (
    get_user,
    get_tgimage,
    update_user
)
from core.logger.logger import get_logger
from loader import bot


log = get_logger()


gen_video_router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent


@gen_video_router.callback_query(F.data.contains("tovideo"))
async def bring_photo_to_life(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    file_id = call.data.split("&&")[1]

    user_db = await get_user(str(call.message.chat.id))
    
    if user_db.get("count_video_generations") <= 0:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Купить",
            callback_data="prices_video"
        )
        await call.message.answer("У вас закончились попытки для генерации видео. 😢", reply_markup=builder.as_markup())
        return
    img_response =  await get_tgimage(int(file_id))
    log.debug(img_response)
    file_info = await bot.get_file(img_response.get("tg_hash"))
    photo_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
    await call.message.answer("""<b>Фото получено!</b> 👌

Начинаю обработку...
<b>Это займет примерно 5 минут</b>""", parse_mode="HTML")
    
    response = await generate_video(call.message.chat.id, photo_url)
    if not response:
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


def setup(dp):
    dp.include_router(gen_video_router)
