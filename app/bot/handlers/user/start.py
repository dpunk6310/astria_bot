# third-party imports
from aiogram import types, Router
from aiogram.filters import CommandStart

from data.messages import use_messages

user_router = Router()

@user_router.message(CommandStart())
@use_messages
async def start_handler(message: types.Message, messages):
    await message.answer(
        messages["start"],
    )
