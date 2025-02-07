from aiogram import Dispatcher

from . import handlers


def setup(dp: Dispatcher):
    handlers.setup(dp)
