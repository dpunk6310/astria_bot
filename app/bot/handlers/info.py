import asyncio
from pathlib import Path

from aiogram import types, Router, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.messages import use_messages
from core.backend.api import (
    create_user_db, 
    get_user,
)
from .utils import (
    create_referal,
    get_main_keyboard,
)


info_router = Router()
BASE_DIR = Path(__file__).resolve().parent.parent


@info_router.message(CommandStart())
@use_messages
async def start_handler(message: types.Message, messages):
    user_db = await get_user(str(message.chat.id))
    if not user_db:
        user_db = await create_user_db(
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
            callback_data="first_payment"
        ),
    )
    
    keyboard = builder.as_markup()
    if user_db.get("count_generations") > 3:
        keyboard = get_main_keyboard()
    
    asyncio.create_task(create_referal(user_db, message))
    
    await message.answer_photo(
        photo=types.FSInputFile(BASE_DIR / "media" / "logo_p.png"),
        caption="""<b>Привет! На связи Пингвин бот - усовершенствованная версия популярной нейронки</b> 🐧

Рассказать тебе как здесь все работает? А если ты уже в курсе, нужно просто внести оплату - и вперед!
""",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    

@info_router.callback_query(F.data == "inst")
async def inst_callback(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Все понятно!",
            callback_data="inst_next2"
        ),
    )
    await call.message.answer_photo(
        photo=types.FSInputFile(BASE_DIR / "media" / "90.png"),
        caption="""<b>Пингвин ИИ</b> - это нейросеть, которая учится на твоих фото и создаёт новые <b>фотографии и видео</b> с твоими чертами лица 

<b>Посмотри на результаты</b> 😍""",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    
    
@info_router.callback_query(F.data == "inst_next2")
async def inst_next2_callback(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Дальше!",
            callback_data="inst_next3"
        ),
    )
    await call.message.answer_photo(
        photo=types.FSInputFile(BASE_DIR / "media" / "2.png"),
        caption="Подойдут фотографии любого качества, но студийные могут дать лучший результат!",
        reply_markup=builder.as_markup()
    )
    

@info_router.callback_query(F.data == "inst_next3")
async def inst_next3_callback(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="А сколько стоит?",
            callback_data="inst_next4"
        ),
    )
    await call.message.answer_photo(
        photo=types.FSInputFile(BASE_DIR / "media" / "87.jpg"),
        caption="""<b>Для тебя подготовили два режима на выбор:</b>

1. Режим «Стили», где ты выбираешь кем быть: от ребенка до кинозвезды! 
2. «Режим бога», где ты сам решаешь кем быть! Тебе нужно будет просто описать что ты хочешь в нескольких словах)

Затем оживите полученные <b>фотографии и превратите их в видео</b> по своему желанию! 🤩""",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    
    
@info_router.callback_query(F.data == "inst_next4")
async def inst_next4_callback(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Купить!",
            callback_data="first_payment"
        ),
    )
    await call.message.answer_photo(
        photo=types.FSInputFile(BASE_DIR / "media" / "89.png"),
        caption="""<b>Ты готов(а) создать свои новые фотографии? Тебе нужно будет просто внести оплату и начнём создание новых шедевров!</b>

Поздравляю, тебе повезло, сейчас мы снизили стоимость на 72%: 1 290₽ вместо <s>4 490₽</s>

Оплати сейчас картой РФ, либо зарубежной картой и получи:
✔️ 90 фотографий 
✔️ Неограниченнок количество шаблонов
✔️ 1 модель
✔️ Режим бога
✔️ <b>Оживление полученных фото!</b>

🎁 <b>Если успеешь оплатить за 30 минут, получишь ещё 10 генераций в подарок</b>""",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    
    
@info_router.callback_query(F.data == "home")
async def home_callback(call: types.CallbackQuery):
    user_db = await get_user(str(call.message.chat.id))
    if not user_db:
        user_db = await create_user_db(
            tg_user_id=call.message.from_user.id,
            first_name=call.message.from_user.first_name,
            last_name=call.message.from_user.last_name,
            username=call.message.from_user.username
        )
        
        
    builder = InlineKeyboardBuilder()
    
    builder.add(
        types.InlineKeyboardButton(
            text="Инструкция",
            callback_data="inst"
        ),
        types.InlineKeyboardButton(
            text="Оплатить",
            callback_data="first_payment"
        ),
    )
    
    keyboard = builder.as_markup()
    if user_db.get("count_generations") > 3:
        keyboard = get_main_keyboard()
    
    await call.message.answer_photo(
        photo=types.FSInputFile(BASE_DIR / "media" / "logo_p.png"),
        caption="""<b>Привет! На связи Пингвин бот - усовершенствованная версия популярной нейронки</b> 🐧

Рассказать тебе как здесь все работает? А если ты уже в курсе, нужно просто внести оплату - и вперед!
""",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@info_router.callback_query(F.data == "driving")
async def driving_callback(call: types.CallbackQuery):
    await call.message.answer_photo(
        photo=types.FSInputFile(BASE_DIR / "media" / "87.jpg"),
        caption="""<b>Для тебя подготовили два режима на выбор:</b>

1. Режим «Стили», где ты выбираешь кем быть: от ребенка до кинозвезды! 
2. «Режим бога», где ты сам решаешь кем быть! Тебе нужно будет просто описать что ты хочешь в нескольких словах)

Затем оживите полученные <b>фотографии и превратите их в видео по своему желанию!</b> 🤩""",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
    

def setup(dp):
    dp.include_router(info_router)    
