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
from data.messages import use_messages
from core.backend.api import (
    create_user_db, 
    create_img_path, 
    delete_user_images, 
    get_user_images,
    create_payment,
    get_user,
    get_tunes,
    get_tune,
    create_tune,
    update_user
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


class UploadPhotoState(StatesGroup):
    gender = State()
    effect = State()
    tune_id = State()


@user_router.message(CommandStart())
@use_messages
async def start_handler(message: types.Message, messages):
    await create_user_db(
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
            callback_data="inst_payment"
        ),
    )
    await message.answer(messages["start"], reply_markup=builder.as_markup())
    

@user_router.message(F.media_group_id)
@media_group_handler
async def handle_albums(messages: list[types.Message], state: FSMContext):
    BASE_DIR = Path(__file__).resolve().parent.parent
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
    
    await messages[-1].answer(
        """Мы получили твои фото и запустили разработку твоего персонального аватара, это займёт около 5 минут … 🔄

А ты пока обязательно подпишись на наш канал @…

Там мы публикуем оригинальные идеи стилей и промтов для твоих новых фотографий, а также актуальные новости.
""", 
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
        keyboard = get_main_keyboard()
        await messages[-1].answer(
            """Твой аватар создан ☑️
Теперь можно приступать к генерациям! Для этого нажми на кнопки "Стили" или "Режим бога" внизу экрана.
""", reply_markup=keyboard
        )


@user_router.callback_query(F.data == "avatar")
async def avatar_callback(call: types.CallbackQuery):
    tunes = await get_tunes(str(call.message.chat.id))
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
    await call.message.answer(
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


@user_router.callback_query(F.data == "inst")
async def inst_callback(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Дальше!",
            callback_data="how_price"
        ),
    )
    await call.message.answer(
        text="Подойдут фотографии любого качества, но студийные могут дать лучший результат!",
        reply_markup=builder.as_markup()
    )
    

@user_router.callback_query(F.data == "generations_stat")
async def generations_stat_callback(call: types.CallbackQuery):
    user_db = await get_user(call.message.chat.id)
    builder = InlineKeyboardBuilder()
    builder.button(
        text="100 фото",
        callback_data="photo"
    )
    builder.button(
        text="500 фото",
        callback_data="photo"
    )
    await call.message.answer(
        text="""
У вас {count_gen} генераций!
Рады, что вам понравилось! 
Хотите больше генераций? 📸
Варианты:
* 100 фото: 990₽
* 500 фото: 3710₽ (скидка 25%!)
Выберите свой вариант!
""".format(count_gen=user_db.count_generation),
        reply_markup=builder.as_markup()
    )
    
    
@user_router.callback_query(F.data == "how_price")
async def how_price_callback(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="А сколько стоит?",
        callback_data="inst_payment"
    )
    builder.button(
        text="Попробовать!",
        callback_data="try_it_gen"
    )
    await call.message.answer(
        text="""Наши основатели сделали два режима:

1. С уже готовыми идеями. Там уже 70+ стилей. От принцессы до Халка!
2. Но если ты хочешь что-то свое, есть режим бога, где ты сам решаешь, кем быть! Просто пишешь краткое описание и получаешь крутую картину!""",
        reply_markup=builder.as_markup()
    )
    
    
@user_router.callback_query(F.data == "try_it_gen")
async def try_it_gen_callback(call: types.CallbackQuery):
    keyboard = get_main_keyboard()
    await call.message.answer(
        text="""Главное меню""",
        reply_markup=keyboard
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
    if user_db.get("is_learn_model"):
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
    
    
@user_router.callback_query(F.data == "styles_effect")
async def styles_effect_callback(call: types.CallbackQuery, state: FSMContext):
    
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
        text="""Выберите эффект""",
        reply_markup=builder.as_markup()
    )
    
    
@user_router.callback_query(F.data == "inst_payment")
async def inst_payment_callback(call: types.CallbackQuery):
    сount_generations = 100
    amount = 100
    payment_id = random.randint(999, 99999)
    await create_payment(
        tg_user_id=str(call.message.chat.id),
        amount=str(amount),
        payment_id=str(payment_id),
        сount_generations=сount_generations,
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
        text="""Теперь самое время перейти к оплате! Можно оплатить как с карты РФ, так и с зарубежной.

Сейчас мы снизили стоимость на 52%! 
1390₽ вместо 2890₽

И за это ты получаешь:
✔️ 100 фотографий
✔️ 100 стилей на ваш выбор
✔️ 1 модель
✔️ режим бога!""",
        reply_markup=builder.as_markup()
    )


@user_router.callback_query(F.data == "home")
async def home_callback(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Инструкция",
            callback_data="inst"
        ),
        types.InlineKeyboardButton(
            text="Оплатить",
            callback_data="inst_payment"
        ),
    )
    await call.message.answer("Привет! На связи Пингвин бот. \nРассказать тебе как здесь все работает?\nЕсли ты уже в курсе, нужно просто внести оплату - и вперед!\n\nНаши преимущества перед другими ботами:\nВместо 25 шаблонов - неограниченное количество\nК каждому фото в «Стили» ты можешь добавить фильтры\nЧат-бот ассистент который поможет составить промт из загруженого фото\nРеферальная система: приглашай друзей и получай бесплатные генерации\nЦена всего 990 руб.\n", reply_markup=builder.as_markup())

    
@user_router.callback_query(F.data.contains("_effect"))
async def handle_effect_handler(call: types.CallbackQuery, state: FSMContext):
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    json_file = BASE_DIR / "media" / "promts.json"
    effect = call.data
    await state.update_data(effect=effect)
    
    data = await state.get_data()
    
    gender: str = data.get("gender")
    if not gender:
        tunes = await get_tunes(str(call.message.chat.id))
        if not tunes:
            await call.message.answer("У Вас нет аватара, создайте его!", reply_markup=get_main_keyboard())
            return
        gender = tunes[0].get("gender")
        tune_id = tunes[0].get("tune_id")
        await state.update_data(gender=gender, tune_id=tune_id)
    
    data = await state.get_data()
    log.debug(data)
    categories = get_categories(gender=gender, json_file=json_file)
    builder = InlineKeyboardBuilder()
    for c in categories:
        builder.button(
            text=c.get("name"),
            callback_data=c.get("slug")
        )
    builder.adjust(2,2,2,2,2)
    builder.button(
        text="На главную",
        callback_data="home"
    )
    # builder.adjust(2, 2, 3, repeat=True)
    await call.message.answer(text="""Выбери понравившийся стиль и фильтр, получите 3 фото через 60 секунд.

В каждом стиле содержится неограниченное количество фотографий, которые выбираются случайным образом.
""", reply_markup=builder.as_markup())
    

    
@user_router.callback_query(F.data.contains("category_"))
async def handle_category_handler(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    effect: str = data.get("effect")
    gender: str = data.get("gender")
    tune_id: int = data.get("tune_id")
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    json_file = BASE_DIR / "media" / "promts.json"
    
    user_db = await get_user(str(call.message.chat.id))
    if user_db.get("count_generations") < 3:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Купить",
            callback_data="inst_payment"
        )
        await call.message.answer("У вас недостаточно генераций", reply_markup=builder.as_markup()) 
        return
    
    category_slug = call.data
    
    if not gender:
        tunes = await get_tunes(str(call.message.chat.id))
        if not tunes:
            await call.message.answer("У Вас нет аватара, создайте его!", reply_markup=get_main_keyboard())
            return
        gender = tunes[0].get("gender")
        tune_id = tunes[0].get("tune_id")
        await state.update_data(gender=gender, tune_id=tune_id)
    log.debug(tune_id)
    if not effect:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Выбрать",
            callback_data="styles_effect"
        )
        await call.message.answer("У вас не выбран эффект", reply_markup=builder.as_markup())
        return
        
    user_prompt = get_random_prompt(json_file=json_file, gender=gender, category_slug=category_slug)
        
    if effect != "no_effect":
        effect = effect.split("_")[0]
    else:
        effect = None
    gen_response = await generate_images(
        tune_id=int(tune_id), 
        promt=user_prompt,
        effect=effect
    )
    
    if not gen_response or "id" not in gen_response:
        await call.message.answer("❌ Ошибка при запуске генерации изображений.")
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
        
    user_db = await get_user(str(call.message.chat.id))
    new_count_gen = user_db.get("count_generations") - 3
    upd_res = await update_user(str(call.message.chat.id), count_generations=new_count_gen)
    log.debug(upd_res)
    await bot.send_media_group(chat_id=call.message.chat.id, media=media_group.build())
    
    await delete_user_images(str(call.message.chat.id))
    
    
def get_main_keyboard():
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Стили", callback_data="styles_effect"), types.InlineKeyboardButton(text="Режим бога", callback_data="god_mod")],
            [types.InlineKeyboardButton(text="Аватар", callback_data="avatar"), types.InlineKeyboardButton(text="Генерации", callback_data="generations_stat")],
            [types.InlineKeyboardButton(text="Настройки", callback_data="settings"), types.InlineKeyboardButton(text="Служба заботы", callback_data="service")],
        ],
    )