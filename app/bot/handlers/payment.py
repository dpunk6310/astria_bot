import random
import json
import asyncio
from pathlib import Path

from aiogram import types, Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger as log

from data.config import ROBOKASSA_MERCHANT_ID, ROBOKASSA_PASSWORD1
from core.utils.robo import generate_payment_link
from core.backend.api import (
    create_payment,
    get_user,
    get_price_list,    
    get_payment,
)


payment_router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent


@payment_router.callback_query(F.data == "prices_photo")
async def prices_photo_callback(call: types.CallbackQuery):
    price_list = await get_price_list("photo")
    builder = InlineKeyboardBuilder()
    price_str = ""
    user_db = await get_user(str(call.message.chat.id))
    for i in price_list:
        if i.get("learn_model"):
            continue
        sale = i.get("sale", None)
        builder.button(
            text=f"{i.get('count')} фото",
            callback_data=f"inst_payment_{i.get('price')}_{i.get('count')}_{user_db.get('is_learn_model')}_0"
        )
        if not sale or sale == "":
            price_str += f"* {i.get('count')} фото: {i.get('price')}₽\n"
        else:
            price_str += f"* {i.get('count')} фото: {i.get('price')}₽ ({sale})\n"
    builder.adjust(2, 2, 2)
    await call.message.answer(
        text="""
Рады, что вам понравилось! 
Хотите больше генераций? 📸
Варианты:
{price_str}
Выберите свой вариант!

""".format(price_str=price_str),
        reply_markup=builder.as_markup()
    )
    
    
@payment_router.callback_query(F.data == "prices_video")
async def prices_video_callback(call: types.CallbackQuery):
    price_list = await get_price_list("video")
    builder = InlineKeyboardBuilder()
    price_str = ""
    user_db = await get_user(str(call.message.chat.id))
    for i in price_list:
        sale = i.get("sale", None)
        if i.get("count") == 1:
            builder.button(
                text=f"{i.get('count')} оживление",
                callback_data=f"inst_payment_{i.get('price')}_0_{user_db.get('is_learn_model')}_{i.get('count')}"
            )
        else:
            builder.button(
                text=f"{i.get('count')} оживлений",
                callback_data=f"inst_payment_{i.get('price')}_0_{user_db.get('is_learn_model')}_{i.get('count')}"
            )
        if not sale or sale == "":
            price_str += f"* {i.get('count')} видео: {i.get('price')}₽\n"
        else:
            price_str += f"* {i.get('count')} видео: {i.get('price')}₽ ({sale})\n"
    builder.adjust(2, 2, 2)
    await call.message.answer(
        text="""
Рады, что вам понравилось! 
Хотите больше генераций? 📹
Варианты:
{price_str}
Выберите свой вариант!

""".format(price_str=price_str),
        reply_markup=builder.as_markup()
    )


@payment_router.callback_query(F.data.contains("first_payment"))
async def first_payment_callback(call: types.CallbackQuery):
    user_db = await get_user(str(call.message.chat.id))
    amount = 1290
    сount_generations = 100
    learn_model = user_db.get("is_learn_model", True)

    while True:
        payment_id = random.randint(10, 214748347)
        pay_db = await get_payment(str(payment_id))
        if pay_db:
            continue
        break
    asyncio.create_task(create_payment(
        tg_user_id=str(call.message.chat.id),
        amount=str(amount),
        payment_id=str(payment_id),
        сount_generations=сount_generations,
        learn_model=learn_model,
        is_first_payment=True,
        count_video_generations=1
    ))
    file_path = BASE_DIR / "media" / "payload.json"
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    index = 0
    description = ""
    for i, v in enumerate(data):
        if v.get("Cost") == amount and v.get("Name") == "Стартовая покупка":
            index = i
            description = v.get("Name")
            break
    payment_link = generate_payment_link(
        ROBOKASSA_MERCHANT_ID,
        ROBOKASSA_PASSWORD1,
        amount,
        int(payment_id),
        description + f" {call.message.chat.id}",
        items=[data[index]],
    )
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Карта РФ",
        url=payment_link
    )
    builder.button(
        text="Зарубежная карта",
        url=payment_link
    )
    builder.button(
        text="Служба поддержки",
        callback_data="support"
    )
    builder.adjust(1,1,1)
    await call.message.answer(
        text="""Нажимая кнопку ниже, вы подтверждаете свое согласие с Политикой конфиденциальности и публичной офертой: 

👉 <b>Политика конфиденциальности:</b> https://photopingvin.space/politics

👉 <b>Публичная оферта:</b> https://photopingvin.space/services

👉 <b>Стоимость услуг:</b> https://photopingvin.space/

Теперь самое время перейти к оплате! Можно оплатить как с карты РФ, так и с зарубежной.""",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    
    
@payment_router.callback_query(F.data.contains("reminders_"))
async def reminders_callback(call: types.CallbackQuery):
    user_db = await get_user(str(call.message.chat.id))
    call_data = call.data.split("_")
    amount = int(call_data[1])
    сount_generations = int(call_data[2])
    сount_video_generations = int(call_data[3])
    learn_model = user_db.get("is_learn_model", True)

    while True:
        payment_id = random.randint(10, 214748347)
        pay_db = await get_payment(str(payment_id))
        if pay_db:
            continue
        break
    asyncio.create_task(create_payment(
        tg_user_id=str(call.message.chat.id),
        amount=str(amount),
        payment_id=str(payment_id),
        сount_generations=сount_generations,
        learn_model=learn_model,
        is_first_payment=True,
        count_video_generations=сount_video_generations
    ))
    file_path = BASE_DIR / "media" / "payload.json"
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    index = 0
    description = ""
    for i, v in enumerate(data):
        if v.get("Cost") == amount and v.get("Name") == "Акция 1" or v.get("Name") == "Акция 2":
            index = i
            description = description + f" {call.message.chat.id}"
            break
    payment_link = generate_payment_link(
        ROBOKASSA_MERCHANT_ID,
        ROBOKASSA_PASSWORD1,
        amount,
        int(payment_id),
        description + f" {call.message.chat.id}",
        items=[data[index]],
    )
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Карта РФ",
        url=payment_link
    )
    builder.button(
        text="Зарубежная карта",
        url=payment_link
    )
    builder.button(
        text="Служба поддержки",
        callback_data="support"
    )
    builder.adjust(1,1,1)
    await call.message.answer(
        text="""Нажимая кнопку ниже, вы подтверждаете свое согласие с Политикой конфиденциальности и публичной офертой: 

👉 <b>Политика конфиденциальности:</b> https://photopingvin.space/politics

👉 <b>Публичная оферта:</b> https://photopingvin.space/services

👉 <b>Стоимость услуг:</b> https://photopingvin.space/

Теперь самое время перейти к оплате! Можно оплатить как с карты РФ, так и с зарубежной.""",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

 
@payment_router.callback_query(F.data.contains("inst_payment"))
async def inst_payment_callback(call: types.CallbackQuery):
    data = call.data.split("_")
    amount = int(data[2])
    сount_generations = int(data[3])
    learn_model = data[4]
    count_video_generations = int(data[5])

    while True:
        payment_id = random.randint(10, 214748347)
        pay_db = await get_payment(str(payment_id))
        if pay_db:
            continue
        break
    asyncio.create_task(create_payment(
        tg_user_id=str(call.message.chat.id),
        amount=str(amount),
        payment_id=str(payment_id),
        сount_generations=сount_generations,
        learn_model=learn_model,
        is_first_payment=False,
        count_video_generations=count_video_generations,
    ))
    file_path = BASE_DIR / "media" / "payload.json"
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    index = None
    description = ""
    for i, v in enumerate(data):
        if v.get("Cost") == amount and v.get("Name") != "Стартовая покупка" and \
            v.get("Name") != "Акция 1" and v.get("Name") != "Акция 2" and v.get("Name"):
            index = i
            description = v.get("Name")
            break
    payment_link = generate_payment_link(
        ROBOKASSA_MERCHANT_ID,
        ROBOKASSA_PASSWORD1,
        amount,
        int(payment_id),
        description + f" {call.message.chat.id}",
        items=[data[index]],
    )
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Карта РФ",
        url=payment_link
    )
    builder.button(
        text="Зарубежная карта",
        url=payment_link
    )
    builder.button(
        text="Служба поддержки",
        callback_data="support"
    )
    builder.adjust(1,1,1)
    await call.message.answer(
        text="""Теперь самое время перейти к оплате! Можно оплатить как с карты РФ, так и с зарубежной.""",
        reply_markup=builder.as_markup()
    )
    

def setup(dp):
    dp.include_router(payment_router)   
