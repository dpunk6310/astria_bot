import asyncio
from pathlib import Path

from aiogram import types, Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.backend.api import (
    get_user,
    get_tunes,
    update_user,
)

from .utils import (
    run_generation_photo,
    generate_photos_helper,
    get_main_keyboard,
)
from core.generation.utils import get_categories


gen_photo_router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent


@gen_photo_router.message(F.text == "Генерации")
async def generations_stat_callback(message: types.Message):
    user_db = await get_user(message.chat.id)
    builder = InlineKeyboardBuilder()
    builder.button(
        text="💳 Докупить фото",
        callback_data="prices_photo"
    )
    builder.button(
        text="💳 Докупить оживление фото",
        callback_data="prices_video"
    )
    builder.adjust(1, 1, 1)
    await message.answer(
        text="""
<b>Спасибо что ты с нами, ты такой талантливый! А талантливым людям надо держаться вместе</b> 🖖🤝❤️

У тебя осталось генераций фото: <b>{count_gen}</b>
У тебя осталось генераций видео: <b>{count_video_generations}</b>
""".format(count_gen=user_db.get("count_generations"), count_video_generations=user_db.get("count_video_generations")),
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
  
    
@gen_photo_router.message(F.text == "Стили")
async def styles_effect_handler(message: types.Message):
    user_db = await get_user(str(message.chat.id))
    if user_db.get("god_mod"):
        await message.answer(text="Режим бога выключен", reply_markup=get_main_keyboard())
        asyncio.create_task(
            update_user(
                str(message.chat.id), 
                god_mod=False, 
                god_mod_text=None,
            )
        )
    
    if user_db.get("count_generations") < 3:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Купить",
            callback_data="prices_photo"
        )
        await message.answer("У вас недостаточно генераций", reply_markup=builder.as_markup()) 
        return
    
    json_file = BASE_DIR / "media" / "promts.json"
    tunes = await get_tunes(str(message.chat.id))
    if not tunes or not user_db.get("gender"):
        builder = InlineKeyboardBuilder()
        builder.button(
            text=f"Добавить аватар",
            callback_data=f"start_upload_photo"
        )
        await message.answer("У Вас нет аватара, создайте его!", reply_markup=builder.as_markup())
        return

    categories = get_categories(gender=user_db.get("gender"), json_file=json_file)
    builder = InlineKeyboardBuilder()
    for c in categories:
        builder.button(
            text=c.get("name"),
            callback_data=c.get("slug")
        )
    builder.adjust(2, 2, 2, 2, 2, repeat=True)
    builder.button(
        text="На главную",
        callback_data="home"
    )
    await message.answer(text="""Выбери понравившийся стиль и фильтр, получите 3 фото через 60 секунд.

В каждом стиле содержится неограниченное количество фотографий, которые выбираются случайным образом.
""", reply_markup=builder.as_markup())

    
@gen_photo_router.callback_query(F.data.contains("_effect"))
async def handle_effect_handler(call: types.CallbackQuery):
    await call.message.delete()
    user_db = await get_user(str(call.message.chat.id))
    effect = call.data
    if not effect:
        effect = "no_effect"
    if effect != "no_effect":
        effect = effect.split("_")[0]
    else:
        effect = None
        
    asyncio.create_task(
        update_user(str(call.message.chat.id), effect=effect)
    )

    tunes = await get_tunes(str(call.message.chat.id))
    if not tunes:
        builder = InlineKeyboardBuilder()
        builder.button(
            text=f"Добавить аватар",
            callback_data=f"start_upload_photo"
        )
        await call.message.answer("У Вас нет аватара, создайте его!", reply_markup=builder.as_markup())
        return

    user_db = await get_user(str(call.message.chat.id))
    if user_db.get("god_mod"):
        if user_db.get("god_mod_text"):
            god_mod_text = f"sks {user_db.get('gender')} {user_db.get('god_mod_text')}"
            await call.message.answer("Создаем ваше фото, немного подождите")
            asyncio.create_task(generate_photos_helper(
                call=call,
                effect=effect,
                tune_id=user_db.get('tune_id') if user_db.get("tune_id") else tunes[0].get("tune_id"),
                user_prompt=god_mod_text
            ))
            asyncio.create_task(
                update_user(str(call.message.chat.id), god_mod_text=None)
            )
            return
        else:
            builder = InlineKeyboardBuilder()
            builder.button(
                text="Инструкция",
                callback_data="inst_god_mod"
            )
            await call.message.answer("Режим бога включен!\n\nВы не ввели текст", reply_markup=builder.as_markup())
            return
    if not user_db.get("tune_id"):
        user_db["tune_id"] = tunes[0].get("tune_id")
    asyncio.create_task(
        run_generation_photo(call, user_db, effect)
    )
    
   
@gen_photo_router.callback_query(F.data.contains("category_"))
async def handle_category_handler(call: types.CallbackQuery):
    asyncio.create_task(
        update_user(
            str(call.message.chat.id), 
            category=call.data
        )
    )
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Киноэффект",
        callback_data="Cinematic_effect"
    )
    builder.button(
        text="Неон",
        callback_data="Neonpunk_effect"
    )
    builder.button(
        text="Без эффекта",
        callback_data="no_effect"
    )
    await call.message.answer(
        text="Выберите эффект",
        reply_markup=builder.as_markup()
    )


def setup(dp):
    dp.include_router(gen_photo_router)
