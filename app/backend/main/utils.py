import asyncio
import random
import string
from pathlib import Path

from loguru import logger as log
from aiogram.exceptions import TelegramAPIError
from aiogram import Bot
from django.conf import settings
from aiogram import types


bot = Bot(token=settings.BOT_TOKEN)

BATCH_SIZE = 10
DELAY_BETWEEN_BATCHES = 0.5
BASE_DIR = Path(__file__).resolve().parent.parent


async def send_messages_reminders(user_ids: list[int], text: str, reply_markup: types.InlineKeyboardMarkup):
    """ Отправляет сообщение о дожимки батчами
    """
    async with bot.session:
        for i in range(0, len(user_ids), BATCH_SIZE):
            batch = user_ids[i:i + BATCH_SIZE]
            tasks = []
            for user_id in batch:
                if reply_markup:
                    tasks.append(_send_message(user_id, text, reply_markup))
            await asyncio.gather(*tasks)
            await asyncio.sleep(DELAY_BETWEEN_BATCHES)
            
            
async def send_messages_newsletters(user_ids: list[int], text: str, photo_url: str = None):
    """ Отправляет сообщение любой рассыки батчами
    """
    async with bot.session:
        for i in range(0, len(user_ids), BATCH_SIZE):
            batch = user_ids[i:i + BATCH_SIZE]
            tasks = []
            for user_id in batch:
                if photo_url:
                    tasks.append(_send_message_photo(user_id, text, None, photo_url=photo_url))
                    continue
                tasks.append(_send_message(user_id, text, None))
            await asyncio.gather(*tasks)
            await asyncio.sleep(DELAY_BETWEEN_BATCHES)


async def _send_message(user_id: int, text: str, reply_markup):
    """ Отправляет сообщение пользователю и обрабатывает ошибки.
    """
    try:
        await bot.send_message(
            user_id, 
            text, 
            parse_mode="HTML", 
            reply_markup=reply_markup
        )
    except TelegramAPIError as e:
        log.error(f"Ошибка при отправке {user_id}: {e}")
        

async def _send_message_photo(user_id: int, text: str, reply_markup, photo_url: str):
    try:
        await bot.send_photo(
            chat_id=user_id, 
            photo=types.FSInputFile(photo_url),
            caption=text, 
            parse_mode="HTML", 
            reply_markup=reply_markup
        )
    except TelegramAPIError as e:
        log.error(f"Ошибка при отправке {user_id}: {e}")


def generate_promo_code(length=8):
    characters = string.ascii_uppercase + string.digits
    promo_code = ''.join(random.choice(characters) for _ in range(length))
    return promo_code