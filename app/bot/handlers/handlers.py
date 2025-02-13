from pathlib import Path
from uuid import uuid4
import random
import os
import json

from aiogram_media_group import media_group_handler
from aiogram import types, Router, F
from aiogram.filters import CommandStart
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger as log

from data.config import ROBOKASSA_MERCHANT_ID, ROBOKASSA_PASSWORD1
from core.utils.robo import generate_payment_link
from core.utils.chatgpt import translate_promt, translate_promt2
from data.messages import use_messages
from core.backend.api import (
    create_user_db, 
    create_img_path, 
    delete_user_images, 
    get_user_images,
    create_payment,
    get_user,
    get_tunes,
    get_price_list,
    create_tune,
    update_user,
    get_avatar_price_list,
    get_payment
)
from core.generation.photo import (
    learn_model_api, 
    wait_for_training, 
    generate_images, 
    wait_for_generation
)
from core.generation.utils import get_categories, get_random_prompt
from loader import bot


user_router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent
BUTTON_TEXTS = {"Стили", "Режим бога", "Выбор аватара", "Генерации", "Доп. опции", "Служба поддержки"}


@user_router.message(CommandStart())
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
        
    log.debug(user_db)
        
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
    
    if not user_db.get("referal"):
        referal = message.text.split(" ")
        if len(referal) == 2:
            referal = referal[1]
            if referal != str(message.chat.id):
                await update_user(str(message.chat.id), referal=referal)
        else:
            referal = None
    
    await message.answer_photo(
        photo=types.FSInputFile(BASE_DIR / "media" / "logo_p.png"),
        caption="""<b>Привет! На связи Пингвин бот - усовершенствованная версия популярной нейронки</b> 🐧

Рассказать тебе как здесь все работает? А если ты уже в курсе, нужно просто внести оплату - и вперед!
""",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    

@user_router.callback_query(F.data == "inst")
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
        caption="""<b>Пингвин ИИ</b> - это нейросеть, которая учится на твоих фото и создаёт новые 📸 с твоими чертами лица 

<b>Посмотри на результаты</b> 😍""",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    
    
@user_router.callback_query(F.data == "inst_next2")
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
    

@user_router.callback_query(F.data == "inst_next3")
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
2. «Режим бога», где ты сам решаешь кем быть! Тебе нужно будет просто описать что ты хочешь в нескольких словах)""",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    
    
@user_router.callback_query(F.data == "inst_next4")
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

🎁 <b>Если успеешь оплатить за 30 минут, получишь ещё 10 генераций в подарок</b>""",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    

@user_router.message(F.media_group_id)
@media_group_handler
async def handle_albums(messages: list[types.Message]):
    user_db = await get_user(messages[-1].chat.id)
    if not user_db.get("is_learn_model"):
        avatar_price_list = await get_avatar_price_list()
        builder = InlineKeyboardBuilder()
        builder.button(
            text=f"{avatar_price_list.get('count')} модель",
            callback_data=f"inst_payment_{avatar_price_list.get('price')}_0_{avatar_price_list.get('learn_model')}"
        )
        # await state.update_data(learn_model=True)
        await messages[-1].answer("Оплатите создание аватара", reply_markup=builder.as_markup())
        return
    log.debug(user_db)
    gender = user_db.get("gender")
    if not gender:
        await messages[-1].answer("Пожалуйста, сначала укажите пол", reply_markup=get_main_keyboard())
        return
    
    photos_path = BASE_DIR / "media" / "photos"
    
    if not os.path.exists(photos_path):
        os.makedirs(photos_path)
    
    if len(messages) != 10:
        await messages[-1].answer("Загрузить можно только 10 фото")
        return
    
    await update_user(tg_user_id=str(messages[0].chat.id), is_learn_model=False, gender=gender)
    
    await messages[-1].answer(
        """Мы получили твои фото и запустили разработку твоего персонального аватара, это займёт около 5-10 минут … 🔄

А ты пока обязательно подпишись на наш канал https://t.me/photopingvin_ai

Там мы публикуем оригинальные идеи стилей и промтов для твоих новых фотографий, а также актуальные новости.
""")
    images = []
    for m in messages:
        if m.photo:
            photo = await bot.get_file(m.photo[-1].file_id)
            file_path = photo.file_path
            output_filename = f"{photos_path}/{uuid4()}_{file_path.replace('photos/', '')}"
            await m.bot.download_file(
                file_path, destination=output_filename
            )
            images.append(output_filename)
            response = await create_img_path(
                tg_user_id=str(m.chat.id),
                path=output_filename
            )
        if m.document:
            photo = await m.bot.get_file(m.document.file_id)
            file_path = photo.file_path
            output_filename = f"{photos_path}/{uuid4()}_{file_path.replace('documents/', '')}"
            images.append(output_filename)
            await m.bot.download_file(
                file_path, destination=output_filename
            )
            response = await create_img_path(
                tg_user_id=str(m.chat.id),
                path=output_filename
            )
    
    images = await get_user_images(str(messages[-1].chat.id))
    imgs = []
    for i in images:
        i = i.get("path")
        imgs.append(i)
    
    response = await learn_model_api(imgs, gender)
    tune_id = response.get("id")
    if not tune_id:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Служба поддержки",
            callback_data="support"
        )
        await messages[-1].answer(
            text="Произошла ошибка во время обучения модели. Пожалуйста, обратитесь в техническую поддержку", 
            reply_markup=builder.as_markup(),
        )
        return
    training_complete = await wait_for_training(tune_id)
    if training_complete:
        response_tune = await create_tune(tune_id=str(tune_id), tg_user_id=str(messages[-1].chat.id), gender=gender)
        log.debug(response_tune)
        await update_user(tg_user_id=str(messages[0].chat.id), is_learn_model=False, tune_id=str(tune_id), gender=None)
        await messages[-1].answer(
            """Твой аватар создан ☑️
Теперь можно приступать к генерациям! Для этого нажми на кнопки "Стили" или "Режим бога" внизу экрана.
""", reply_markup=get_main_keyboard()
        )
        for i in imgs:
            try:
                os.remove(i)
            except Exception as err:
                log.error(err)
                continue


@user_router.message(F.text == "Выбор аватара")
async def avatar_callback(message: types.Message):
    tunes = await get_tunes(str(message.chat.id))
    log.debug(tunes)
    builder = InlineKeyboardBuilder()
    for i, tune in enumerate(tunes, 1):
        builder.button(
            text=f"Модель {i}",
            callback_data=f"tune_{tune.get('tune_id')}_{i}"
        )
    builder.adjust(1, 1, 1, 1)
    builder.button(
        text=f"Добавить аватар",
        callback_data=f"start_upload_photo"
    )
    await message.answer(
        text="Выберите модель:",
        reply_markup=builder.as_markup()
    )
    
    
@user_router.callback_query(F.data.contains("tune_"))
async def select_avatar_callback(call: types.CallbackQuery):
    tune_id = call.data.split("_")[1]
    tune_num = call.data.split("_")[-1]
    await update_user(tg_user_id=str(call.message.chat.id), tune_id=str(tune_id))
    keyboard = get_main_keyboard()
    await call.message.answer(
        text=f"Смена модели прошла успешно, теперь используется «Модель №{tune_num}» ✅",
        reply_markup=keyboard
    )
    

@user_router.message(F.text == "Генерации")
async def generations_stat_callback(message: types.Message):
    user_db = await get_user(message.chat.id)
    builder = InlineKeyboardBuilder()
    builder.button(
        text="💳 Докупить фото",
        callback_data="prices_photo"
    )
    await message.answer(
        text="""
<b>Спасибо что ты с нами, ты такой талантливый! А талантливым людям надо держаться вместе</b> 🖖🤝❤️

У тебя осталось генераций фото: <b>{count_gen}</b>
""".format(count_gen=user_db.get("count_generations")),
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    
    
@user_router.callback_query(F.data == "prices_photo")
async def prices_photo_callback(call: types.CallbackQuery):
    price_list = await get_price_list()
    builder = InlineKeyboardBuilder()
    price_str = ""
    user_db = await get_user(str(call.message.chat.id))
    for i in price_list:
        log.debug(i)
        if i.get("learn_model"):
            continue
        sale = i.get("sale", None)
        builder.button(
            text=f"{i.get('count')} фото",
            callback_data=f"inst_payment_{i.get('price')}_{i.get('count')}_{user_db.get('is_learn_model')}"
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
    
    
@user_router.callback_query(F.data.in_(["man", "woman"]))
async def gender_selection(call: types.CallbackQuery):
    log.debug(call.data)
    await update_user(str(call.message.chat.id), gender=call.data)
    await call.message.answer_photo(
        photo=types.FSInputFile(BASE_DIR / "media" / "inst.png"),
        caption="""
        <b>ИНСТРУКЦИЯ...</b>

<b>Загрузи 10 фото, чтобы обучить бота и получить доступ к генерации</b> 📲

<b>Важно:</b>
    – Загружайте строго 10 фото. Не 5, не 8 и не 16.
    – Используй крупные планы своего лица или селфи, избегай снимков с дальнего расстояния.
    – На фото должен(на) быть только ты — без родителей, бабушек и домашних животных.
    – Не выбирайте фото с резкими эмоциями, максимум легкая улыбка.
    – Загружай фото в прямой позе, без наклонов головы или шеи.
    – Убедитесь в хорошем освещении фотографии для получения качественного результата.

<b>Загрузить фото и обучить бота можно только один раз! Подходите внимательно к выбору фото и строго следуйте инструкции!</b>

Если iPhone предложит «Конвертировать в JPEG», соглашайся 👍

Теперь просто отправь 10 фотографий в бота ⬇️

        """, parse_mode="HTML")
    
    
@user_router.callback_query(F.data == "start_upload_photo")
async def start_upload_photo_callback(call: types.CallbackQuery):
    user_db = await get_user(str(call.message.chat.id))
    if not user_db.get("is_learn_model"):
        avatar_price_list = await get_avatar_price_list()
        builder = InlineKeyboardBuilder()
        builder.button(
            text=f"{avatar_price_list.get('count')} модель",
            callback_data=f"inst_payment_{avatar_price_list.get('price')}_0_{avatar_price_list.get('learn_model')}"
        )
        await call.message.answer("Оплатите создание аватара", reply_markup=builder.as_markup())
        return
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Мужчина",
        callback_data="man"
    )
    builder.button(
        text="Женщина",
        callback_data="woman"
    )
    await call.message.answer(
        text="""Осталось совсем чуть-чуть ❤️
<b>Для начала выбери пол:</b>""",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
        
        
@user_router.message(F.text == "Режим бога")
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
    god_mod = user_db.get("god_mod", False)
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
    
    
@user_router.callback_query(F.data == "on_god_mod")
async def on_god_mod_callback(call: types.CallbackQuery):
    await update_user(str(call.message.chat.id), god_mod=True)
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
    
    
@user_router.callback_query(F.data == "off_god_mod")
async def off_god_mod_callback(call: types.CallbackQuery):
    await update_user(str(call.message.chat.id), god_mod=False)
    builder = InlineKeyboardBuilder()
    builder.button(
        text="На главную",
        callback_data="home"
    )
    await call.message.answer(
        text="Режим бога выключен!",
        reply_markup=builder.as_markup()
    )
    
    
@user_router.message(~F.text.in_(BUTTON_TEXTS))
async def set_text_in_godmod_callback(message: types.Message):
    if message.text in BUTTON_TEXTS:
        return
    
    user_db = await get_user(str(message.chat.id))
    log.debug(user_db)
    if user_db.get("count_generations") < 3:
        builder = InlineKeyboardBuilder()
        builder.add(
            types.InlineKeyboardButton(
                text="Купить!",
                callback_data="prices_photo"
            ),
        )
        await message.answer("У вас недостаточно генераций", reply_markup=builder.as_markup())
        return
    if not user_db.get("god_mod"):
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Вкл. режим бога",
            callback_data="on_god_mod"
        )
        await message.answer("Сначала включите режим бога", reply_markup=builder.as_markup())
        return
    promt = message.text
    for _ in range(5):
        try:
            promt = translate_promt2(promt)
            if promt:
                break
        except Exception as err:
            log.debug(err)
            continue
    await update_user(str(message.chat.id), god_mod_text=promt)
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
    
    
@user_router.callback_query(F.data == "inst_god_mod")
async def inst_god_mod_callback(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Назад",
        callback_data="god_mod"
    )
    await call.message.answer(
        text="""📝 <b>Инструкция: как создать идеальный запрос для вашего фото?</b>
1️⃣ Укажи какое именно фото вы хотите: портрет, в полный рост и т.д.

2️⃣ Выбери стиль: спортсмен, рок-музыкант, футболист или королева.

3️⃣ Подробно опишите свой стиль: одежду, прическу, аксессуары, черты лица, фигуру

4️⃣ Тщательно сформулируй запрос, описав фон и оформление: что происходит позади тебя, как это должно выглядеть, какая поза у тебя, какое действие происходит на фото.

5️⃣ Избегайте длинных предложений. Каждый запрос вводи кратко, разделяя запятыми.

<b>Действуй по этим правилам и ты получишь свое идеальное фото всего через 30 секунд!</b> ✅
""", reply_markup=builder.as_markup(), parse_mode="HTML")
    
    
@user_router.message(F.text == "Стили")
async def styles_effect_handler(message: types.Message):
    user_db = await get_user(str(message.chat.id))
    if user_db.get("god_mod"):
        await message.answer(text="Режим бога выключен", reply_markup=get_main_keyboard())
        await update_user(str(message.chat.id), god_mod=False, god_mod_text=None)
    
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
    # builder.adjust(2, 2, 3, repeat=True)
    await message.answer(text="""Выбери понравившийся стиль и фильтр, получите 3 фото через 60 секунд.

В каждом стиле содержится неограниченное количество фотографий, которые выбираются случайным образом.
""", reply_markup=builder.as_markup())
    

@user_router.callback_query(F.data.contains("first_payment"))
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
    await create_payment(
        tg_user_id=str(call.message.chat.id),
        amount=str(amount),
        payment_id=str(payment_id),
        сount_generations=сount_generations,
        learn_model=learn_model,
        is_first_payment=True
    )
    file_path = BASE_DIR / "media" / "payload.json"
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    index = 0
    description = ""
    for i, v in enumerate(data):
        if v.get("Cost") == amount:
            index = i
            description = v.get("Name")
            break
    payment_link = generate_payment_link(
        ROBOKASSA_MERCHANT_ID,
        ROBOKASSA_PASSWORD1,
        amount,
        int(payment_id),
        description,
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
        # text="Теперь самое время перейти к оплате! Можно оплатить с карты РФ",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

 
@user_router.callback_query(F.data.contains("inst_payment"))
async def inst_payment_callback(call: types.CallbackQuery):
    data = call.data.split("_")
    amount = int(data[2])
    сount_generations = int(data[3])
    learn_model = data[4]
    # user_db = await get_user(str(call.message.chat.id))
    # learn_model = user_db.get("is_learn_model")

    while True:
        payment_id = random.randint(10, 214748347)
        pay_db = await get_payment(str(payment_id))
        if pay_db:
            continue
        break
    await create_payment(
        tg_user_id=str(call.message.chat.id),
        amount=str(amount),
        payment_id=str(payment_id),
        сount_generations=сount_generations,
        learn_model=learn_model,
        is_first_payment=False,
    )
    file_path = BASE_DIR / "media" / "payload.json"
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    index = 0
    description = ""
    for i, v in enumerate(data):
        if v.get("Cost") == amount:
            index = i
            description = v.get("Name")
            # if learn_model and description != "Создание дополнительной модели":
            #     continue
            break
    payment_link = generate_payment_link(
        ROBOKASSA_MERCHANT_ID,
        ROBOKASSA_PASSWORD1,
        amount,
        int(payment_id),
        description,
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
        # text="Теперь самое время перейти к оплате! Можно оплатить с карты РФ",
        reply_markup=builder.as_markup()
    )


@user_router.callback_query(F.data == "home")
async def home_callback(call: types.CallbackQuery):
    user_db = await get_user(str(call.message.chat.id))
    if not user_db:
        user_db = await create_user_db(
            tg_user_id=call.message.from_user.id,
            first_name=call.message.from_user.first_name,
            last_name=call.message.from_user.last_name,
            username=call.message.from_user.username
        )
        
    log.debug(user_db)
        
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

    
@user_router.callback_query(F.data.contains("_effect"))
async def handle_effect_handler(call: types.CallbackQuery):
    user_db = await get_user(str(call.message.chat.id))
    effect = call.data
    if not effect:
        effect = "no_effect"
    if effect != "no_effect":
        effect = effect.split("_")[0]
    else:
        effect = None
        
    await update_user(str(call.message.chat.id), effect=effect)

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
            
            await generate_photos_helper(
                call=call,
                effect=effect,
                tune_id=user_db.get('tune_id'),
                user_prompt=god_mod_text
            )
            await update_user(str(call.message.chat.id), god_mod_text=None)
            return
        else:
            builder = InlineKeyboardBuilder()
            builder.button(
                text="Инструкция",
                callback_data="inst_god_mod"
            )
            await call.message.answer("Режим бога включен!\n\nВы не ввели текст", reply_markup=builder.as_markup())
            return
    json_file = BASE_DIR / "media" / "promts.json"
    user_prompt = get_random_prompt(json_file=json_file, gender=user_db.get("gender"), category_slug=user_db.get("category"))
    await generate_photos_helper(
        tune_id=user_db.get('tune_id'),
        user_prompt=user_prompt,
        effect=effect,
        call=call
    )
    
   
@user_router.callback_query(F.data.contains("category_"))
async def handle_category_handler(call: types.CallbackQuery):
    await update_user(str(call.message.chat.id), category=call.data)
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
    

async def generate_photos_helper(call: types.CallbackQuery, tune_id: str, user_prompt: str, effect: str):
    user_db = await get_user(str(call.message.chat.id))
    new_count_gen = user_db.get("count_generations") - 3
    await update_user(str(call.message.chat.id), count_generations=new_count_gen)
    
    gen_response = await generate_images(
        tune_id=int(tune_id), 
        promt=user_prompt,
        effect=effect
    )
    if not gen_response or "id" not in gen_response:
        log.error(gen_response)
        await call.message.answer("❌ Ошибка при запуске генерации изображений.", reply_markup=get_main_keyboard())
        new_count_gen = user_db.get("count_generations") + 3
        await update_user(str(call.message.chat.id), count_generations=new_count_gen)
        return

    user_db = await get_user(str(call.message.chat.id))
    prompt_id = gen_response.get("id")
    await call.message.answer("Создаем ваше фото, немного подождите")
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

    image_urls = await wait_for_generation(prompt_id)
    media_group = MediaGroupBuilder(caption='<a href="https://t.me/photopingvin_bot?start">🖼 Создано в Пингвин ИИ</a>')
    
    if image_urls:
        for i in image_urls:
            media_group.add(type="photo", media=i, parse_mode="HTML")
    else:
        await call.message.answer("❌ Ошибка генерации изображения.")
    
    await bot.send_media_group(chat_id=call.message.chat.id, media=media_group.build())
    await delete_user_images(str(call.message.chat.id))


@user_router.message(F.text == "Служба поддержки")
async def callcenter_callback(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="На главную",
        callback_data="home"
    )
    await message.answer(
        """<b>Наша служба поддержки работает в этом Телеграм аккаунте:</b> @managerpingvin_ai

Пожалуйста, детально опишите, что у вас произошло и при необходимости приложите скриншоты - так мы сможем помочь тебе быстрее. Не забудь указать свой Chat ID: <code>{chat_id}</code>""".format(chat_id=message.chat.id),
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@user_router.callback_query(F.data == "support")
async def support_handler(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="На главную",
        callback_data="home"
    )
    await call.message.answer(
    """<b>Наша служба поддержки работает в этом Телеграм аккаунте:</b> @managerpingvin_ai

Пожалуйста, детально опишите, что у вас произошло и при необходимости приложите скриншоты - так мы сможем помочь тебе быстрее. Не забудь указать свой Chat ID: <code>{chat_id}</code>""".format(chat_id=call.message.chat.id),
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@user_router.callback_query(F.data == "driving")
async def driving_callback(call: types.CallbackQuery):
    await call.message.answer_photo(
        photo=types.FSInputFile(BASE_DIR / "media" / "87.jpg"),
        caption="""<b>Для тебя подготовили два режима на выбор:</b>

1. Режим «Стили», где ты выбираешь кем быть: от ребенка до кинозвезды! 
2. «Режим бога», где ты сам решаешь кем быть! Тебе нужно будет просто описать что ты хочешь в нескольких словах)""",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

     
def get_main_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Стили"), types.KeyboardButton(text="Режим бога")],
            [types.KeyboardButton(text="Выбор аватара"), types.KeyboardButton(text="Генерации")],
            # [types.KeyboardButton(text="Доп. опции"), types.KeyboardButton(text="Служба поддержки")],
            [types.KeyboardButton(text="Служба поддержки")],
        ],
        resize_keyboard=True
    )