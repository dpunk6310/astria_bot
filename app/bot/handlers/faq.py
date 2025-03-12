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


faq_router = Router()
BASE_DIR = Path(__file__).resolve().parent.parent
log = get_logger()


async def get_faq(message: types.Message):
    builder = InlineKeyboardBuilder()
    # builder.button(
    #     text="Для чего нужен Пингвин ИИ?",
    #     callback_data="faq_1"
    # )
    # builder.button(
    #     text="Как пользоваться?",
    #     callback_data="faq_2"
    # )
    builder.button(
        text="Частые вопросы",
        callback_data="faq_3"
    )
    builder.button(
        text="Управление подпиской",
        callback_data="faq_subscribe"
    )
    builder.button(
        text="Служба поддержки",
        callback_data="faq_support"
    )
    builder.adjust(1, 1, 1, 1)
    await message.answer("""<b>Добро пожаловать в дополнительное меню</b>

Здесь находиться вся нужна информация о Пингвин ИИ

Если остались вопросы - вы всегда можете обратиться в поддержку""", 
    parse_mode="HTML", reply_markup=builder.as_markup())


@faq_router.message(F.text == "FAQ")
async def faq_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await get_faq(message=message)
    
    
@faq_router.callback_query(F.data == "faq_back")
async def faq_back_callback(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    await get_faq(message=call.message)
    
    
    
@faq_router.callback_query(F.data == "faq_support")
async def faq_support_callback(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Назад",
        callback_data="faq_back"
    )
    await call.message.answer(
    """<b>Наша служба поддержки работает в этом Телеграм аккаунте:</b> @managerpingvin_ai

Пожалуйста, детально опишите, что у вас произошло и при необходимости приложите скриншоты - так мы сможем помочь тебе быстрее. Не забудь указать свой Chat ID: <code>{chat_id}</code>""".format(chat_id=call.message.chat.id),
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    
    
@faq_router.callback_query(F.data == "faq_3")
async def faq_3_callback(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Назад",
        callback_data="faq_back"
    )
    await call.message.answer(
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
Для отмены подписки, пожалуйста, откройте раздел «Управление подпиской»
""",
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )


@faq_router.callback_query(F.data == "faq_subscribe")
async def faq_subscribe_callback(call: types.CallbackQuery):
    await call.message.delete()
    
    status = "🟢 Оформлена"
    user_db = await get_user(str(call.message.chat.id))
    if not user_db.get("subscribe") and not user_db.get("maternity_payment_id"):
        status = "🔴 Не оформлена"
    
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Поддержка",
        callback_data="faq_support"
    )
    builder.button(
        text="Отмена подписки",
        callback_data="drop_subscribe_1"
    )
    builder.button(
        text="Назад",
        callback_data="faq_back"
    )
    
    
    builder.adjust(1, 1, 1)
    await call.message.answer(
        text="""<b>Приветствуем в вашем личном пространстве управления подпиской!</b>

Подписка на Пингвин ИИ – это ваш ключ к созданию потрясающих фото, улучшению их качества и воплощению креативных идей! 📸

Забудьте о дорогостоящих услугах фотографов и дизайнеров – экономьте с умом!

Хотите зарабатывать? Станьте нейро-фотографом с Пингвин ИИ!

Статус подписки: <b>{status}</b>""".format(status=status),
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )



@faq_router.callback_query(F.data == "drop_subscribe_1")
async def drop_subscribe_1_callback(call: types.CallbackQuery):
    await call.message.delete()
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Отменить подписку",
        callback_data="drop_subscribe_2"
    )
    builder.button(
        text="Поддержка",
        callback_data="faq_support"
    )
    builder.button(
        text="Назад",
        callback_data="faq_back"
    )
    builder.adjust(1, 1, 1)
    await call.message.answer(
        text='''{first_name}, вы точно уверены, что хотите отменить подписку?

Если у вас возникли проблемы с качеством, напишите в наш отдел поддержки — мы оперативно поможем и решим вопрос.

Нажмите: "Поддержка".'''.format(first_name=call.message.chat.first_name),
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )


@faq_router.callback_query(F.data == "drop_subscribe_2")
async def drop_subscribe_2_callback(call: types.CallbackQuery):
    await call.message.delete()
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
        text="""{first_name}, ваша подписка успешно отменена

Нам очень жаль с вами расставаться, поэтому предлагаем разовые пакеты генераций. 😔""".format(first_name=call.message.chat.first_name),
        parse_mode="HTML"
    )
    await get_prices_photo(call=call)


def setup(dp):
    dp.include_router(faq_router)    
