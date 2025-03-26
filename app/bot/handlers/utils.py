import asyncio

from aiogram import types

from core.generation.pfp import generate_pfp_v2
from core.backend.api import (
    get_user,
    update_user,
    get_price_list,
)
from core.generation.train import create_train
from core.logger.logger import get_logger
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.utils.chatgpt import translate_promt2
from core.generation.photo_v2 import (
    generate_images_v2
)
from loader import bot


log = get_logger()


async def create_referal(user_db: dict, message: types.Message) -> dict:
    if not user_db.get("referal"):
        referal = message.text.split(" ")
        if len(referal) == 2:
            referal = referal[1]
            if referal != str(message.chat.id):
                await update_user(data={
                    "tg_user_id": str(message.chat.id),
                    "referal": referal,
                })

        
async def get_user_url_images(m: types.Message):
    if m.photo:
        photo = await bot.get_file(m.photo[-1].file_id)
        file_path = photo.file_path
        return f"https://api.telegram.org/file/bot{bot.token}/{file_path}"
    if m.document:
        photo = await m.bot.get_file(m.document.file_id)
        file_path = photo.file_path
        return f"https://api.telegram.org/file/bot{bot.token}/{file_path}"

        
async def process_learning(
    messages: list[types.Message],
    gender: str,
    name: str
):
    builder = InlineKeyboardBuilder()
    
    img_urls = []
    for m in messages:
        url = await get_user_url_images(m)
        img_urls.append(url)
        
    response = await create_train(
        gender=gender, 
        chat_id=messages[0].chat.id, 
        images=img_urls,
        name=name
    )
    
    if not response:
        builder.button(
            text="Служба поддержки",
            callback_data="support"
        )
        await messages[-1].answer(
            text="Произошла ошибка во время обучения модели. Пожалуйста, обратитесь в техническую поддержку. Код ошибки: 2", 
            reply_markup=builder.as_markup(),
        )
        log.error(f"Ошибка в обучении модели. UserID={messages[-1].chat.id} | Gender={gender} Код ошибки: 2")
        await update_user(data={
            "tg_user_id": str(messages[0].chat.id), 
            "is_learn_model": True
        })
        
        return
    

async def save_promt(message: types.Message):
    promt = translate_promt2(message.text)
    await update_user(data={
        "tg_user_id": str(message.chat.id), 
        "god_mod_text": promt, 
    })
    
    
async def generate_photo_from_photo_helper(call: types.CallbackQuery, user_db: dict, image_url: str, effect: str):
    default_gen_count = 2
    default_deduct_count = default_gen_count * 2

    user_gen_count = user_db.get("count_generations", 0)

    if user_gen_count >= default_deduct_count:
        count_gen = default_gen_count
        deduct_gen = default_deduct_count
    else:
        count_gen = 1
        deduct_gen = 2

    if user_gen_count >= deduct_gen:
        new_count_gen = user_gen_count - deduct_gen
        asyncio.create_task(
            update_user(data={
                "tg_user_id": str(call.message.chat.id), 
                "count_generations": new_count_gen, 
            })
        )
    else:
        builder = InlineKeyboardBuilder()
        builder.button(
            text=f"Купить",
            callback_data=f"prices_photo"
        )
        await call.message.answer(f"У Вас недостаточно генераций: {user_db.get('count_generations', 0)} 😱", reply_markup=builder.as_markup())
        return
    
    await call.message.answer(f"""<b>Фото получено!</b> 👌

Начинаю обработку...
<b>Это займет примерно 55 секунд</b>""", parse_mode="HTML")
    gen_response = await generate_pfp_v2(
        image_url=image_url,
        chat_id=call.message.chat.id,
        effect=effect,
        tune_id=int(user_db.get("tune_id")),
        gender=user_db.get("gender")
    )
    if not gen_response:
        await call.message.answer("❌ Ошибка при запуске генерации изображений. Код ошибки 21.", reply_markup=get_main_keyboard())
        log.error(f"Ошибка при запуске генерации изображений | UserID={call.message.chat.id} | Response = {gen_response} | Код ошибки: 21")
        new_count_gen = user_db.get("count_generations") + count_gen
        asyncio.create_task(
            update_user(data={
                "tg_user_id": str(call.message.chat.id), 
                "count_generations": new_count_gen, 
            })
        )
        return

    user_db = await get_user(str(call.message.chat.id))
    if user_db.get("count_generations") < 3:
        await call.message.answer("""
<b>У Вас осталось {count_gen} генераций!</b>

Получи эксклюзивный доступ к миру ИИ-фотографии!  🎁  

<b>Мы дарим дополнительные генерации в нашем боте!</b>

🎁 Как получить 10 бесплатных генераций:

1. Подпишись на наш Instagram: https://www.instagram.com/photopingvin.ai
2. Поделись своим волшебным ИИ-фото в Stories.
3. Отметь нас @photopingvin.ai и добавь кликабельную ссылку на бота: https://t.me/photopingvin_bot?start={user_tg_id}

🎁 <b>Хочешь 30 бесплатных генераций?</b>

1. Создай совместный пост (функция Соавторство) с нашим аккаунтом @photopingvin.ai
2. Поделись своими потрясающими ИИ-фотографиями и расскажи о своих впечатлениях!

<b>Отправь скриншот своей публикации в поддержку @managerpingvin_ai – и мы начислим бонусные генерации на твой аккаунт!  Ждём твои креативные работы!</b>

*Instagram принадлежит компании Meta, признанной экстремистской организацией и запрещенной в РФ""".format(
    count_gen=user_db.get("count_generations"), user_tg_id=str(call.message.chat.id)), parse_mode="HTML",
)
    
    
async def generate_photos_helper(call: types.CallbackQuery, tune_id: str, user_prompt: str, effect: str):
    await call.message.answer(text="Создаем ваше фото, немного подождите", parse_mode="HTML")
    user_db = await get_user(str(call.message.chat.id))
    count_gen = 3
    if 0 < user_db.get("count_generations", 0) < 3:
        count_gen = user_db.get("count_generations")
    new_count_gen = user_db.get("count_generations") - count_gen
    asyncio.create_task(
        update_user(data={
            "tg_user_id": str(call.message.chat.id), 
            "count_generations": new_count_gen, 
        })
    )
    gen_response = await generate_images_v2(
        tune_id=int(tune_id), 
        prompt=user_prompt,
        effect=effect,
        chat_id=call.message.chat.id
    )
    if not gen_response:
        await call.message.answer("❌ Ошибка при запуске генерации изображений. Код ошибки 1.", reply_markup=get_main_keyboard())
        log.error(f"Ошибка при запуске генерации изображений | UserID={call.message.chat.id} | User promt:{user_prompt} | Response = {gen_response} | Код ошибки: 1")
        new_count_gen = user_db.get("count_generations") + count_gen
        asyncio.create_task(
            update_user(data={
                "tg_user_id": str(call.message.chat.id), 
                "count_generations": new_count_gen, 
            })
        )
        return

    user_db = await get_user(str(call.message.chat.id))
    if user_db.get("count_generations") < 3:
        await call.message.answer("""
<b>У Вас осталось {count_gen} генераций!</b>

Получи эксклюзивный доступ к миру ИИ-фотографии!  🎁  

<b>Мы дарим дополнительные генерации в нашем боте!</b>

🎁 Как получить 10 бесплатных генераций:

1. Подпишись на наш Instagram: https://www.instagram.com/photopingvin.ai
2. Поделись своим волшебным ИИ-фото в Stories.
3. Отметь нас @photopingvin.ai и добавь кликабельную ссылку на бота: https://t.me/photopingvin_bot?start={user_tg_id}

🎁 <b>Хочешь 30 бесплатных генераций?</b>

1. Создай совместный пост (функция Соавторство) с нашим аккаунтом @photopingvin.ai
2. Поделись своими потрясающими ИИ-фотографиями и расскажи о своих впечатлениях!

<b>Отправь скриншот своей публикации в поддержку @managerpingvin_ai – и мы начислим бонусные генерации на твой аккаунт!  Ждём твои креативные работы!</b>

*Instagram принадлежит компании Meta, признанной экстремистской организацией и запрещенной в РФ""".format(
    count_gen=user_db.get("count_generations"), user_tg_id=str(call.message.chat.id)), parse_mode="HTML",
)


async def get_prices_photo(call: types.CallbackQuery, drop_subscribe: bool = False):
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
    text = """
Рады, что вам понравилось! 
Хотите больше генераций? 📸
Варианты:
{price_str}
<b>Выберите свой вариант!</b>

Если у вас есть промокод, введите его в <b>сообщение</b> ниже.
""".format(price_str=price_str)
    if drop_subscribe:
        text = """
Хотите больше генераций? 📸
Варианты:
{price_str}
Выберите свой вариант!
""".format(price_str=price_str)
    await call.message.answer(
        text=text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


def get_main_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Стили"), types.KeyboardButton(text="Режим бога")],
            [types.KeyboardButton(text="Выбор аватара"), types.KeyboardButton(text="Фото по фото")],
            [types.KeyboardButton(text="Генерации"), types.KeyboardButton(text="Служба поддержки")],
            [types.KeyboardButton(text="Партнёрская программа"), types.KeyboardButton(text="FAQ")],
            [types.KeyboardButton(text="Подарить Пингвин ИИ")],
        ],
        resize_keyboard=True
    )
