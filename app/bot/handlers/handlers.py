from pathlib import Path
from uuid import uuid4
import random
import os

from aiogram_media_group import media_group_handler
from aiogram import types, Router, F
from aiogram.filters import CommandStart
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger as log

from data.config import ROBOKASSA_MERCHANT_ID, ROBOKASSA_TEST_PASSWORD1
from core.utils.robokassa import generate_payment_link
from core.utils.chatgpt import translate_promt
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


class UploadPhotoState(StatesGroup):
    gender = State()
    effect = State()
    tune_id = State()
    god_mod_text = State()
    category = State()
    

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
        
    builder = InlineKeyboardBuilder()
    
    builder.add(
        types.InlineKeyboardButton(
            text="Инструкция",
            callback_data="inst"
        ),
        types.InlineKeyboardButton(
            text="Оплатить",
            callback_data="prices_photo"
        ),
    )
    
    keyboard = builder.as_markup()
    if user_db.get("count_generations") > 3:
        keyboard = get_main_keyboard()
    
    await message.answer_photo(
        photo=types.FSInputFile(BASE_DIR / "media" / "logo_p.png"),
        caption="""<b>Привет! На связи Пингвин бот - усовершенствованная версия популярной нейронки</b> 🐧

Рассказать тебе как здесь все работает? А если ты уже в курсе, нужно просто внести оплату - и вперед!

Кстати, мои преимущества:
🧊 Неограниченное количество шаблонов
🧊 Фильтры к каждому фото в «Стили»
🧊 Каждое фото ты можешь оживить в видео 🎞️ 
🧊 Чат-бот ассистент помогает составить промт* из загруженого фото
🧊 Удобная реферальная система: приглашай друзей и получай бесплатные генерации 
🧊 Цена всего 1299 руб. ❣️

*промт - это текстовый запрос пользователя к нейросети""",
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
        photo=types.FSInputFile(BASE_DIR / "media" / "90.jpg"),
        caption="""<b>Пингвин ИИ</b> - это нейросеть, которая учится на твоих фото и создаёт новые 📸 с твоими чертами лица 

<b>Посмотри на результаты</b> 😍👇""",
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
        photo=types.FSInputFile(BASE_DIR / "media" / "86.jpg"),
        caption="Подойдут фотографии любого качества, но студийные могут дать лучший результат!",
        reply_markup=builder.as_markup()
    )
    
    
@user_router.callback_query(F.data == "inst_next3")
async def inst_next3_callback(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Дальше!",
            callback_data="inst_next4"
        ),
    )
    await call.message.answer_photo(
        photo=types.FSInputFile(BASE_DIR / "media" / "87.jpg"),
        caption="Фотки нужны самые обычные. Но если будут студийные, результат по моим наблюдениям, может быть лучше!",
        reply_markup=builder.as_markup()
    )


@user_router.callback_query(F.data == "inst_next4")
async def inst_next4_callback(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="А сколько стоит?",
            callback_data="inst_next5"
        ),
    )
    await call.message.answer_photo(
        photo=types.FSInputFile(BASE_DIR / "media" / "85.jpg"),
        caption="""<b>Для тебя подготовили два режима на выбор:</b>

1. Режим «Стили», где ты выбираешь кем быть: от ребенка до кинозвезды! 
2. «Режим бога», где ты сам решаешь кем быть! Тебе нужно будет просто описать что ты хочешь в нескольких словах)""",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    
    
@user_router.callback_query(F.data == "inst_next5")
async def inst_next5_callback(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Купить!",
            callback_data="prices_photo"
        ),
    )
    await call.message.answer_photo(
        photo=types.FSInputFile(BASE_DIR / "media" / "89.jpg"),
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
async def handle_albums(messages: list[types.Message], state: FSMContext):
    user_db = await get_user(messages[-1].chat.id)
    if not user_db.get("is_learn_model"):
        avatar_price_list = await get_avatar_price_list()
        builder = InlineKeyboardBuilder()
        builder.button(
            text=f"{avatar_price_list.get('count')} модель",
            callback_data=f"inst_payment_{avatar_price_list.get('price')}_0_{avatar_price_list.get('learn_model')}"
        )
        await messages[-1].answer("Оплатите создание аватара", reply_markup=builder.as_markup())
        return
    
    data = await state.get_data()
    gender = data.get("gender")
    if not gender:
        await messages[-1].answer("Пожалуйста, сначала укажите пол")
        return
    
    photos_path = BASE_DIR / "media" / "photos"
    
    if not os.path.exists(photos_path):
        os.makedirs(photos_path)
    
    if len(messages) != 10:
        await messages[-1].answer("Загрузить можно только 10 фото")
        return
    
    await messages[-1].answer(
        """Мы получили твои фото и запустили разработку твоего персонального аватара, это займёт около 5-10 минут … 🔄

А ты пока обязательно подпишись на наш канал https://t.me/photopingvin_ai

Там мы публикуем оригинальные идеи стилей и промтов для твоих новых фотографий, а также актуальные новости.
""")
    
    await update_user(tg_user_id=str(messages[0].chat.id), is_learn_model=False)
    
    for m in messages:
        if m.photo:
            photo = await bot.get_file(m.photo[-1].file_id)
            file_path = photo.file_path
            output_filename = f"{photos_path}/{uuid4()}_{file_path.replace('photos/', '')}"
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
    training_complete = await wait_for_training(tune_id)
    if training_complete:
        response_tune = await create_tune(tune_id=str(tune_id), tg_user_id=str(messages[-1].chat.id), gender=gender)
        log.debug(response_tune)
        await state.update_data(tune_id=tune_id)
        await messages[-1].answer(
            """Твой аватар создан ☑️
Теперь можно приступать к генерациям! Для этого нажми на кнопки "Стили" или "Режим бога" внизу экрана.
""", reply_markup=get_main_keyboard()
        )


@user_router.message(F.text == "Выбор аватара")
async def avatar_callback(message: types.Message):
    tunes = await get_tunes(str(message.chat.id))
    log.debug(tunes)
    builder = InlineKeyboardBuilder()
    for i, tune in enumerate(tunes, 1):
        builder.button(
            text=f"Модель {i}",
            callback_data=f"tune_{tune.get('tune')}_{i}"
        )
    builder.button(
        text=f"Добавить аватар",
        callback_data=f"start_upload_photo"
    )
    builder.adjust(3, 3, 3, 1)
    await message.answer(
        text="Выберите модель:",
        reply_markup=builder.as_markup()
    )
    
    
@user_router.callback_query(F.data.contains("tune_"))
async def select_avatar_callback(call: types.CallbackQuery, state: FSMContext):
    tune_id = call.data.split("_")[1]
    tune_num = call.data.split("_")[-1]
    await state.update_data(tune_id=tune_id)
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
async def gender_selection(call: types.CallbackQuery, state: FSMContext):
    gender = call.data
    await state.update_data(gender=gender)
    await call.message.answer("""
        ИНСТРУКЦИЯ...

Загрузи 10 фото, чтобы обучить бота и получить доступ к генерации 📲

Важно:
    – Загружайте строго 10 фото. Не 5, не 8 и не 16.
    – Используй крупные планы своего лица или селфи, избегай снимков с дальнего расстояния.
    – На фото должен(на) быть только ты — без родителей, бабушек и домашних животных.
    – Не выбирайте фото с резкими эмоциями, максимум легкая улыбка.
    – Загружай фото в прямой позе, без наклонов головы или шеи.
    – Убедитесь в хорошем освещении фотографии для получения качественного результата.

Загрузить фото и обучить бота можно только один раз! Подходите внимательно к выбору фото и строго следуйте инструкции!

Если iPhone предложит «Конвертировать в JPEG», соглашайся 👍

Теперь просто отправь 10 фотографий в бота ⬇️

        """)
    
    
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
        text="""Укажите свой пол""",
        reply_markup=builder.as_markup()
    )
        
        
@user_router.message(F.text == "Режим бога")
async def god_mod_callback(message: types.Message):
    tunes = await get_tunes(str(message.chat.id))
    if not tunes:
        await message.answer("У Вас нет аватара, создайте его!", reply_markup=get_main_keyboard())
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
async def set_text_in_godmod_callback(message: types.Message, state: FSMContext):
    if message.text in BUTTON_TEXTS:
        # await bot.delete_message(message.chat.id, message.message_id)
        return
    
    user_db = await get_user(str(message.chat.id))
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
            promt = translate_promt(promt)
            if promt:
                break
        except Exception as err:
            log.debug(err)
            continue
    await state.update_data(god_mod_text=promt)
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
        text="""📝 Инструкция: как создать идеальный запрос для вашего фото?
1️⃣ Укажи какое именно фото вы хотите: портрет, в полный рост и т.д.
2️⃣ Выбери стиль: спортсмен, рок-музыкант, футболист или королева.
3️⃣ Подробно опишите свой стиль: одежду, прическу, аксессуары, черты лица, фигуру
4️⃣ Тщательно сформулируй запрос, описав фон и оформление: что происходит позади тебя, как это должно выглядеть, какая поза у тебя, какое действие происходит на фото.
5️⃣ Избегайте длинных предложений. Каждый запрос вводи кратко, разделяя запятыми.
Действуй по этим правилам и ты получишь свое идеальное фото всего через 30 секунд! ✅
""")
    
    
@user_router.message(F.text == "Стили")
async def styles_effect_handler(message: types.Message, state: FSMContext):
    user_db = await get_user(str(message.chat.id))
    if user_db.get("god_mod"):
        await message.answer(text="Вы в режиме бога!", reply_markup=get_main_keyboard())
        return
    
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
    if not tunes:
        await message.answer("У Вас нет аватара, создайте его!", reply_markup=get_main_keyboard())
        return
    gender = tunes[0].get("gender")
    tune_id = tunes[0].get("tune_id")
    await state.update_data(gender=gender, tune_id=tune_id)
    
    categories = get_categories(gender=gender, json_file=json_file)
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
    
    
@user_router.callback_query(F.data.contains("inst_payment"))
async def inst_payment_callback(call: types.CallbackQuery):
    data = call.data.split("_")
    amount = int(data[2])
    сount_generations = int(data[3])
    learn_model = data[4]
    
    log.debug(amount)
    log.debug(сount_generations)
    log.debug(learn_model)

    payment_id = random.randint(999, 99999)
    await create_payment(
        tg_user_id=str(call.message.chat.id),
        amount=str(amount),
        payment_id=str(payment_id),
        сount_generations=сount_generations,
        learn_model=learn_model
    )
    payment_link = generate_payment_link(
        ROBOKASSA_MERCHANT_ID,
        ROBOKASSA_TEST_PASSWORD1,
        amount,
        int(payment_id),
        f"{payment_id}",
        is_test=1,
    )
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Карта РФ",
        url=payment_link
    )
    builder.button(
        text="На главную",
        callback_data="home"
    )
    await call.message.answer(
        text="""Теперь самое время перейти к оплате! Можно оплатить как с карты РФ, так и с зарубежной.""",
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
        
    builder = InlineKeyboardBuilder()
    
    builder.add(
        types.InlineKeyboardButton(
            text="Инструкция",
            callback_data="inst"
        ),
        types.InlineKeyboardButton(
            text="Оплатить",
            callback_data="prices_photo"
        ),
    )
    
    keyboard = builder.as_markup()
    if user_db.get("count_generations") > 3:
        keyboard = get_main_keyboard()
    
    await call.message.answer_photo(
        photo=types.FSInputFile(BASE_DIR / "media" / "logo_p.png"),
        caption="""<b>Привет! На связи Пингвин бот - усовершенствованная версия популярной нейронки</b> 🐧

Рассказать тебе как здесь все работает? А если ты уже в курсе, нужно просто внести оплату - и вперед!

Кстати, мои преимущества:
🧊 Неограниченное количество шаблонов
🧊 Фильтры к каждому фото в «Стили»
🧊 Каждое фото ты можешь оживить в видео 🎞️ 
🧊 Чат-бот ассистент помогает составить промт* из загруженого фото
🧊 Удобная реферальная система: приглашай друзей и получай бесплатные генерации 
🧊 Цена всего 1299 руб. ❣️

*промт - это текстовый запрос пользователя к нейросети""",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

    
@user_router.callback_query(F.data.contains("_effect"))
async def handle_effect_handler(call: types.CallbackQuery, state: FSMContext):
    effect = call.data
    if not effect:
        effect = "no_effect"
    if effect != "no_effect":
        effect = effect.split("_")[0]
    else:
        effect = None

    data = await state.get_data()

    tunes = await get_tunes(str(call.message.chat.id))
    if not tunes:
        await call.message.answer("У Вас нет аватара, создайте его!", reply_markup=get_main_keyboard())
        return
    gender = tunes[0].get("gender")
    tune_id = tunes[0].get("tune_id")
    data = await state.update_data(gender=gender, tune_id=tune_id)

    # data = await state.get_data()
    user_db = await get_user(str(call.message.chat.id))
    if user_db.get("god_mod"):
        if data.get("god_mod_text"):
            god_mod_text = f"sks {gender} {data.get('god_mod_text')}"
            
            await generate_photos_helper(
                call=call,
                effect=effect,
                tune_id=tune_id,
                user_prompt=god_mod_text
            )
            await state.update_data(god_mod_text=None)
            return
        else:
            builder = InlineKeyboardBuilder()
            builder.button(
                text="Инструкция",
                callback_data="inst_god_mod"
            )
            await call.message.answer("Вы не ввели текст", reply_markup=builder.as_markup())
            return
    json_file = BASE_DIR / "media" / "promts.json"
    user_prompt = get_random_prompt(json_file=json_file, gender=gender, category_slug=data.get("category"))
    await generate_photos_helper(
        tune_id=tune_id,
        user_prompt=user_prompt,
        effect=effect,
        call=call
    )
    
   
@user_router.callback_query(F.data.contains("category_"))
async def handle_category_handler(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(category=call.data)
        
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
    #  data = await state.get_data()
    # effect: str = data.get("effect")
    # gender: str = data.get("gender")
    # tune_id: int = data.get("tune_id")
    
    # json_file = BASE_DIR / "media" / "promts.json"

    
    # if not gender:
    #     tunes = await get_tunes(str(call.message.chat.id))
    #     if not tunes:
    #         await call.message.answer("У Вас нет аватара, создайте его!", reply_markup=get_main_keyboard())
    #         return
    #     gender = tunes[0].get("gender")
    #     tune_id = tunes[0].get("tune_id")
    #     await state.update_data(gender=gender, tune_id=tune_id)
        
    # user_prompt = get_random_prompt(json_file=json_file, gender=gender, category_slug=category_slug)
    
    # if effect != "no_effect":
    #     effect = effect.split("_")[0]
    # else:
    #     effect = None
    # await generate_photos_helper(
    #     tune_id=tune_id,
    #     user_prompt=user_prompt,
    #     effect=effect,
    #     call=call
    # )


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
        return

    prompt_id = gen_response["id"]
    await call.message.answer("Создаем ваше фото, немного подождите")

    image_urls = await wait_for_generation(prompt_id)
    media_group = MediaGroupBuilder(caption="🖼 Ваши фото успешно сгенерированы")
    
    if image_urls:
        for i in image_urls:
            media_group.add(type="photo", media=i)
    else:
        await call.message.answer("❌ Ошибка генерации изображения.")
    
    await bot.send_media_group(chat_id=call.message.chat.id, media=media_group.build())
    await delete_user_images(str(call.message.chat.id))


@user_router.message(F.text == "Служба поддержки")
async def callcenter_callback(message: types.Message):
    await message.answer(
        """<b>Наша служба поддержки работает в этом Телеграм аккаунте:</b> @managerpingvin_ai

Пожалуйста, детально опишите, что у вас произошло и при необходимости приложите скриншоты - так мы сможем помочь тебе быстрее""",
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