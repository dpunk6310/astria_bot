import asyncio
from pathlib import Path

from aiogram import types, Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.backend.api import (
    get_user,
    get_tunes,
    update_user,
)
from core.logger.logger import get_logger

from .utils import save_promt


log = get_logger()

god_mod_router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent
BUTTON_TEXTS = {
    "Стили", 
    "Режим бога", 
    "Выбор аватара", 
    "Генерации", 
    "Доп. опции", 
    "Служба поддержки", 
    "Аккаунт",
}


@god_mod_router.message(F.text == "Режим бога")
async def god_mod_callback(message: types.Message):
    tunes = await get_tunes(str(message.chat.id))
    if not tunes:
        builder = InlineKeyboardBuilder()
        builder.button(
            text=f"Добавить аватар",
            callback_data=f"start_upload_photo"
        )
        await message.answer("У Вас нет аватара, создайте его!", reply_markup=builder.as_markup())
        return
    user_db = await get_user(str(message.chat.id))
    god_mod = user_db.get("god_mod")
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Инструкция",
        callback_data="inst_god_mod"
    )
    if god_mod:
        builder.button(
            text="Выкл. режим бога",
            callback_data="off_god_mod"
        )
    else:
        builder.button(
            text="Вкл. режим бога",
            callback_data="on_god_mod"
        )
    await message.answer(
        text="Управление режимом бога 💫",
        reply_markup=builder.as_markup()
    )
    
    
@god_mod_router.callback_query(F.data == "on_god_mod")
async def on_god_mod_callback(call: types.CallbackQuery):
    asyncio.create_task(
        update_user(str(call.message.chat.id), god_mod=True)
    )
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Инструкция",
        callback_data="inst_god_mod"
    )
    builder.button(
        text="На главную",
        callback_data="home"
    )
    await call.message.answer(
        text="""Режим бога активирован! Просто напиши мне описание, какое фото ты хочешь получить, и он создаст для тебя желанный образ.
*Чтобы получить более точный результат, ознакомься с инструкцией по созданию идеальных запросов ⬇️
""",
        reply_markup=builder.as_markup()
    )
    
    
@god_mod_router.callback_query(F.data == "off_god_mod")
async def off_god_mod_callback(call: types.CallbackQuery):
    asyncio.create_task(
        update_user(str(call.message.chat.id), god_mod=False)
    )
    builder = InlineKeyboardBuilder()
    builder.button(
        text="На главную",
        callback_data="home"
    )
    await call.message.answer(
        text="Режим бога выключен!",
        reply_markup=builder.as_markup()
    )
    
    
@god_mod_router.message(~F.text.in_(BUTTON_TEXTS))
async def set_text_in_godmod_callback(message: types.Message):
    if message.text in BUTTON_TEXTS:
        return
    
    user_db = await get_user(str(message.chat.id))
    # if user_db.get("count_generations") < 3:
    #     builder = InlineKeyboardBuilder()
    #     builder.add(
    #         types.InlineKeyboardButton(
    #             text="Купить!",
    #             callback_data="prices_photo"
    #         ),
    #     )
    #     await message.answer("У вас недостаточно генераций", reply_markup=builder.as_markup())
    #     return
    if not user_db.get("god_mod"):
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Вкл. режим бога",
            callback_data="on_god_mod"
        )
        await message.answer("Сначала включите режим бога", reply_markup=builder.as_markup())
        return
    
    if not user_db.get("tune_id"):
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Выбрать",
            callback_data="set_avatar"
        )
        await message.answer("Пожалуйста выберите аватар", reply_markup=builder.as_markup())
        return

    await save_promt(message)

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
    await message.answer(
        text="Ваш промт сохранен",
        reply_markup=builder.as_markup()
    )
    

@god_mod_router.callback_query(F.data == "inst_god_mod")
async def inst_god_mod_callback(call: types.CallbackQuery):
    await call.message.answer(
        text="""📝 <b>Инструкция: как создать идеальный запрос для вашего фото?</b>
1️⃣ Укажи какое именно фото вы хотите: портрет, в полный рост и т.д.

2️⃣ Выбери стиль: спортсмен, рок-музыкант, футболист или королева.

3️⃣ Подробно опишите свой стиль: одежду, прическу, аксессуары, черты лица, фигуру

4️⃣ Тщательно сформулируй запрос, описав фон и оформление: что происходит позади тебя, как это должно выглядеть, какая поза у тебя, какое действие происходит на фото.

5️⃣ Избегайте длинных предложений. Каждый запрос вводи кратко, разделяя запятыми.

<b>Действуй по этим правилам и ты получишь свое идеальное фото всего через 30 секунд!</b> ✅
""", parse_mode="HTML")
    

def setup(dp):
    dp.include_router(god_mod_router)
