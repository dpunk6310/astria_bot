from aiogram import Dispatcher

from . import user


def setup(dp: Dispatcher):
    user.setup(dp)
