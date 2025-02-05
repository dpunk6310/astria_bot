# third-party imports
from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram import Router

# locale imports
from .start import start_handler

user_router = Router()

def setup(dp: Dispatcher):
    user_router.message(

    )
    dp.register_message_handler(
        start_handler,
        CommandStart(),
    )
