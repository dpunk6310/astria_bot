import asyncio
from pathlib import Path

from aiogram import types, Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from core.backend.api import (
    get_user,
    get_tunes,
    update_user,
    get_categories
)
from .utils import (
    run_generation_photo,
    generate_photos_helper,
    get_main_keyboard,
    generate_photo_from_photo_helper,
)
from loader import bot


class PhotoFromPhoto(StatesGroup):
    photo = State()


gen_photo_router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent


@gen_photo_router.message(F.text == "Генерации")
async def generations_stat_callback(message: types.Message, state: FSMContext):
    await state.clear()
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
async def styles_effect_handler(message: types.Message, state: FSMContext):
    await state.clear()
    user_db = await get_user(str(message.chat.id))
    if user_db.get("god_mod"):
        await message.answer(text="Режим бога выключен", reply_markup=get_main_keyboard())
        asyncio.create_task(
            update_user(data={
                "tg_user_id": str(message.chat.id),
                "god_mod": False,
                "god_mod_text": None
            })
        )

    tunes = await get_tunes(str(message.chat.id))
    if not tunes or not user_db.get("gender"):
        builder = InlineKeyboardBuilder()
        builder.button(
            text=f"Добавить аватар",
            callback_data=f"start_upload_photo"
        )
        await message.answer("У Вас нет аватара, создайте его!", reply_markup=builder.as_markup())
        return

    categories = await get_categories(gender=user_db.get("gender"))
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
    
    
async def inst_photo_from_photo_handler(message: types.Message, state: FSMContext):
    await state.set_state(PhotoFromPhoto.photo)
    user_db = await get_user(str(message.chat.id))
    
    if user_db.get("god_mod"):
        await message.answer(text="Режим бога выключен", reply_markup=get_main_keyboard())
        asyncio.create_task(
            update_user(data={
                "tg_user_id": str(message.chat.id),
                "god_mod": False,
                "god_mod_text": None
            })
        )

    tunes = await get_tunes(str(message.chat.id))
    if not tunes or not user_db.get("gender"):
        builder = InlineKeyboardBuilder()
        builder.button(
            text=f"Добавить аватар",
            callback_data=f"start_upload_photo"
        )
        await message.answer("У Вас нет аватара, создайте его!", reply_markup=builder.as_markup())
        return

    await message.answer_photo(
        photo=types.FSInputFile(BASE_DIR / "media" / "198.png"),
        caption="""<b>Перевоплотись в стиле любимого фото!</b> 🤩

— <b>Отправь фото</b>, которое хочешь повторить.
— Получи 2 эксклюзивных фото в этом стиле, <b>но с твоим аватаром!</b>

Стоимость: За 2 фото, спишется 4 генерации.

👇 Отправь фото, которое хочешь повторить👇
""", parse_mode="HTML")
    
    
@gen_photo_router.message(F.text == "Фото по фото")
async def start_gen_photo_from_photo_handler(message: types.Message, state: FSMContext):
    await inst_photo_from_photo_handler(message, state)


@gen_photo_router.callback_query(F.data == "inst_photo_from_photo")
async def start_gen_photo_from_photo_callback(call: types.CallbackQuery, state: FSMContext):
    await inst_photo_from_photo_handler(call.message, state)
    
    
@gen_photo_router.message(PhotoFromPhoto.photo, F.photo)
async def handle_photo(message: types.Message, state: FSMContext):
    user_db = await get_user(str(message.chat.id))
    
    if user_db.get("count_generations", 0) < 2:
        builder = InlineKeyboardBuilder()
        builder.button(
            text=f"Купить",
            callback_data=f"prices_photo"
        )
        await message.answer(f"У Вас недостаточно генераций: {user_db.get('count_generations')} 😱", reply_markup=builder.as_markup())
        return
    photo = message.photo[-1]
    file_id = photo.file_id
    await state.update_data(file_id=file_id)

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
        text="Портретный",
        callback_data="Photographic_effect"
    )
    builder.button(
        text="Без эффекта",
        callback_data="no_effect"
    )
    
    builder.adjust(1, 1, 1, 1)
    await message.answer(
        text="""<b>Фото получено!</b> 👌

Выберите эффект""",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@gen_photo_router.callback_query(StateFilter(PhotoFromPhoto.photo), F.data.contains("effect"))
async def handle_effect_photo_to_photo_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    
    data = await state.get_data()
    file_id = data.get("file_id")
    
    # if file_id is None:
    #     await call.message.answer("Error: File ID is missing. Please try again.")
    #     return
    
    file_info = await bot.get_file(file_id)
    image_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
    
    effect = call.data
    if not effect:
        effect = "no_effect"
    if effect != "no_effect":
        effect = effect.split("_")[0]
    else:
        effect = None
        
    asyncio.create_task(
        update_user(data={
            "tg_user_id": str(call.message.chat.id),
            "effect": effect,
        })
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

    if not user_db.get("tune_id"):
        user_db["tune_id"] = tunes[0].get("tune_id")
        user_db["gender"] = tunes[0].get("gender")
        asyncio.create_task(
            update_user(data={
                "tg_user_id": str(call.message.chat.id),
                "tune_id": user_db["tune_id"],
                "gender": user_db["gender"]
            })
        )
    asyncio.create_task(
        generate_photo_from_photo_helper(call=call, user_db=user_db, effect=effect, image_url=image_url)
    )
    
    await state.clear()

    
@gen_photo_router.callback_query(F.data.contains("_effect"))
async def handle_effect_handler(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    user_db = await get_user(str(call.message.chat.id))
    if user_db.get("count_generations") == 0:
        builder = InlineKeyboardBuilder()
        builder.button(
            text=f"Купить",
            callback_data=f"prices_photo"
        )
        await call.message.answer("У Вас недостаточно генераций😱", reply_markup=builder.as_markup())
        return
    effect = call.data
    if not effect:
        effect = "no_effect"
    if effect != "no_effect":
        effect = effect.split("_")[0]
    else:
        effect = None
    
    asyncio.create_task(
        update_user(data={
            "tg_user_id": str(call.message.chat.id),
            "effect": effect,
        })
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
                update_user(data={
                    "tg_user_id": str(call.message.chat.id),
                    "god_mod_text": None,
                })
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
async def handle_category_handler(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    asyncio.create_task(
        update_user(data={
            "tg_user_id": str(call.message.chat.id),
            "category": call.data,
        })
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
        text="Портретный",
        callback_data="Photographic_effect"
    )
    builder.button(
        text="Без эффекта",
        callback_data="no_effect"
    )
    
    builder.adjust(1, 1, 1, 1)
    await call.message.answer(
        text="Выберите эффект",
        reply_markup=builder.as_markup()
    )


def setup(dp):
    dp.include_router(gen_photo_router)
