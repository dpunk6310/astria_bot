import json
import functools
from aiogram import types
import os


def load_messages():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(base_dir, "messages.json")
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


def use_messages(handler):
    @functools.wraps(handler)
    async def wrapper(message: types.Message, *args, **kwargs):
        MESSAGES = load_messages()
        return await handler(message, MESSAGES, *args, **kwargs)
    return wrapper
