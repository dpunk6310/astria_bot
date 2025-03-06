import asyncio
from pathlib import Path

from aiogram_media_group import media_group_handler
from aiogram import types, Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from core.backend.api import (
    get_user,  
    update_user,
    get_avatar_price_list,
    get_tunes,
    get_tune
)

from .utils import (
    get_user_url_images,
    process_learning,
    get_main_keyboard,
)


avatar_router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent

class LearnModel(StatesGroup):
    photo = State()


@avatar_router.callback_query(F.data.contains("tune_"))
async def select_avatar_callback(call: types.CallbackQuery):
    tune_id = call.data.split("_")[1]
    tune_num = call.data.split("_")[-1]
    tune = await get_tune(str(tune_id))
    asyncio.create_task(
        update_user(tg_user_id=str(call.message.chat.id), tune_id=str(tune_id), gender=tune.get("gender"))
    )
    keyboard = get_main_keyboard()
    await call.message.answer(
        text=f"Смена модели прошла успешно, теперь используется «Модель №{tune_num}» ✅",
        reply_markup=keyboard
    )
    
    
@avatar_router.callback_query(F.data == "set_avatar")
async def avatar_callback(call: types.CallbackQuery):
    tunes = await get_tunes(str(call.message.chat.id))
    if not tunes:
        builder = InlineKeyboardBuilder()
        builder.button(
            text=f"Добавить аватар",
            callback_data=f"start_upload_photo"
        )
        await call.message.answer("У Вас нет аватара, создайте его!", reply_markup=builder.as_markup())
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
    await call.message.answer(
        text="Выберите модель:",
        reply_markup=builder.as_markup()
    )


@avatar_router.message(F.text == "Выбор аватара")
async def avatar_handler(message: types.Message):
    tunes = await get_tunes(str(message.chat.id))
    if not tunes:
        builder = InlineKeyboardBuilder()
        builder.button(
            text=f"Добавить аватар",
            callback_data=f"start_upload_photo"
        )
        await message.answer("У Вас нет аватара, создайте его!", reply_markup=builder.as_markup())
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


@avatar_router.message(F.media_group_id, LearnModel.photo)
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
    gender = user_db.get("gender")
    if not gender:
        await messages[-1].answer("Пожалуйста, сначала укажите пол", reply_markup=get_main_keyboard())
        return
    
    if len(messages) != 10:
        await messages[-1].answer("Загрузить можно только 10 фото")
        return
    
    asyncio.create_task(
        update_user(
            tg_user_id=str(messages[0].chat.id), 
            is_learn_model=False, 
            gender=gender
        )
    )
    
    await state.clear()
    
    await messages[-1].answer(
        """Мы получили твои фото и запустили разработку твоего персонального аватара, это займёт около 5-10 минут … 🔄

А ты пока обязательно подпишись на наш канал https://t.me/photopingvin_ai

Там мы публикуем оригинальные идеи стилей и промтов для твоих новых фотографий, а также актуальные новости.
""")
    img_urls = []
    for m in messages:
        url = await get_user_url_images(m)
        img_urls.append(url)
        
    asyncio.create_task(process_learning(messages, img_urls, gender))
    

@avatar_router.callback_query(F.data.in_(["man", "woman"]))
async def gender_selection(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(LearnModel.photo)
    asyncio.create_task(
        update_user(str(call.message.chat.id), gender=call.data)
    )
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
    
    
@avatar_router.callback_query(F.data == "start_upload_photo")
async def start_upload_photo_callback(call: types.CallbackQuery):
    user_db = await get_user(str(call.message.chat.id))
    if not user_db.get("is_learn_model"):
        avatar_price_list = await get_avatar_price_list()
        builder = InlineKeyboardBuilder()
        builder.button(
            text=f"{avatar_price_list.get('count')} модель",
            callback_data=f"inst_payment_{avatar_price_list.get('price')}_0_{avatar_price_list.get('learn_model')}_0"
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


def setup(dp):
    dp.include_router(avatar_router)
