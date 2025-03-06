from aiogram import types, Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext


support_router = Router()


@support_router.message(F.text == "Служба поддержки")
async def callcenter_callback(message: types.Message, state: FSMContext):
    await state.clear()
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


@support_router.callback_query(F.data == "support")
async def support_handler(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
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
    

def setup(dp):
    dp.include_router(support_router)   
