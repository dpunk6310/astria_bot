import asyncio
from pathlib import Path

from aiogram import types, Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.messages import use_messages
from core.backend.api import (
    create_user_db, 
    get_user,
    update_user,
)
from core.logger.logger import get_logger
from .utils import (
    create_referal,
    get_main_keyboard,
    get_prices_photo
)


info_router = Router()
BASE_DIR = Path(__file__).resolve().parent.parent
log = get_logger()


@info_router.message(CommandStart())
@use_messages
async def start_handler(message: types.Message, messages, state: FSMContext):
    await state.clear()
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
    if user_db.get("has_purchased", True) and user_db.get("count_generations", 0) > 0:
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
async def inst_callback(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
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
async def inst_next2_callback(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
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
async def inst_next3_callback(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
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
async def inst_next4_callback(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Купить!",
            callback_data="first_payment"
        ),
    )
    user_db = await get_user(str(call.message.chat.id))
    if user_db.get("referal") == "691579474":
        await call.message.answer_photo(
        photo=types.FSInputFile(BASE_DIR / "media" / "192.jpg"),
        caption="""<b>Ты готов(а) создать свои новые фотографии? Тебе нужно будет просто внести оплату и начнём создание новых шедевров!</b>

Поздравляю, тебе повезло! Сейчас мы снизили стоимость ежемесячной подписки на 70%: всего 990 вместо <s>4 490₽</s>!

Оплати сейчас картой РФ, либо зарубежной картой и получи:
✔️ 80 фотографий 
✔️ Неограниченнок количество шаблонов
✔️ 1 модель
✔️ Режим бога
✔️ Оживление полученных фото!
✔️ Перевоплощение в стиле любого фото! 🤩

🎁<b> Если успеешь оплатить за 30 минут, получишь ещё 10 генераций в подарок</b>

👉 Политика конфиденциальности: https://photopingvin.space/politics

👉 Публичная оферта: https://photopingvin.space/services

👉 Стоимость услуг: https://photopingvin.space/
""",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
        return
    await call.message.answer_photo(
        photo=types.FSInputFile(BASE_DIR / "media" / "193.jpg"),
        caption="""<b>Ты готов(а) создать свои новые фотографии? Тебе нужно будет просто внести оплату и начнём создание новых шедевров!</b>

Поздравляю, тебе повезло! Сейчас мы снизили стоимость ежемесячной подписки на 70%: всего 1390₽ вместо <s>4 490₽</s>!

Оплати сейчас картой РФ, либо зарубежной картой и получи:
✔️ 90 фотографий 
✔️ Неограниченнок количество шаблонов
✔️ 1 модель
✔️ Режим бога
✔️ Оживление полученных фото!
✔️ Перевоплощение в стиле любого фото! 🤩

🎁<b> Если успеешь оплатить за 30 минут, получишь ещё 10 генераций в подарок</b>

👉 Политика конфиденциальности: https://photopingvin.space/politics

👉 Публичная оферта: https://photopingvin.space/services

👉 Стоимость услуг: https://photopingvin.space/
""",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    
    
@info_router.callback_query(F.data == "home")
async def home_callback(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
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
    if user_db.get("count_generations") > 0:
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
async def driving_callback(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer_photo(
        photo=types.FSInputFile(BASE_DIR / "media" / "87.jpg"),
        caption="""<b>Для тебя подготовили два режима на выбор:</b>

1. Режим «Стили», где ты выбираешь кем быть: от ребенка до кинозвезды! 
2. «Режим бога», где ты сам решаешь кем быть! Тебе нужно будет просто описать что ты хочешь в нескольких словах)

Затем оживите полученные <b>фотографии и превратите их в видео по своему желанию!</b> 🤩""",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
    

@info_router.message(F.text == "FAQ")
async def faq_handler(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Отменить подписку",
        callback_data="drop_subscribe_1"
    )
    await message.answer(
        text="""<b>Часто задаваемые вопросы:</b>

<b>Остаются ли мои фото и аватар конфиденциальными?</b>
Абсолютно! Ваши фотографии и созданные на их основе модели используются исключительно вами и хранятся с максимальной степенью защиты.

<b>Как быстро создаются фотографии?</b>
Получайте 3 готовых изображения всего за 40-50 секунд!

<b>Какие способы оплаты доступны?</b>
Мы принимаем карты практически всех стран мира через безопасные, лицензированные платежные системы, полностью соответствующие законам.

<b>Есть ли бесплатный пробный период?</b>
К сожалению, нет.  Высокая производительность нашей нейросети требует значительных вычислительных мощностей, что делает бесплатный доступ невозможным.

<b>Насколько реалистичны получаемые изображения?</b>
Созданные ИИ фотографии поразительно реалистичны.  Многие клиенты используют их даже в своих профессиональных резюме!

<b>Что происходит после оплаты?</b>
После оплаты вы получаете доступ к личному кабинету, где сможете загружать фото, создавать новые изображения и управлять своей подпиской.

<b>Сколько стилей доступно?</b>
Сейчас доступно более 100 уникальных стилей! Вы сможете изучить все варианты после создания своего аватара.

<b>Есть ли реферальная программа?</b>
Конечно! Приглашайте друзей и получайте вознаграждение: 30 бесплатных генераций за каждого друга, оплатившего подписку.  Создайте свою реферальную ссылку в личном кабинете после оплаты.

<b>Как отменить подписку?</b>
Для отмены подписки, пожалуйста, свяжитесь с нашим менеджером: @managerpingvin_ai""",
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )
    
@info_router.callback_query(F.data == "drop_subscribe_1")
async def drop_subscribe_1_callback(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Оставить подписку",
        callback_data="home"
    )
    builder.button(
        text="Отменить подписку",
        callback_data="drop_subscribe_2"
    )
    await call.message.answer(
        text="Вы уверены?",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    
    
@info_router.callback_query(F.data == "drop_subscribe_2")
async def drop_subscribe_2_callback(call: types.CallbackQuery):
    # user_db = await get_user(str(call.message.chat.id))
    # if not user_db.get("maternity_payment_id"):
    asyncio.create_task(
        update_user(data={
            "tg_user_id": str(call.message.chat.id),
            "maternity_payment_id": None,
            "subscribe": None
        })
    )
    await call.message.answer(
        text="Ваша подписка отменена!",
        parse_mode="HTML"
    )
    await get_prices_photo(call=call)
    

def setup(dp):
    dp.include_router(info_router)    
