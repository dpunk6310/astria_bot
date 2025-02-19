from datetime import timedelta
import asyncio

from loguru import logger as log
from aiogram.exceptions import TelegramAPIError
from aiogram import Bot
from django.conf import settings
from django.utils.timezone import now

from config import celery_app
from celery import shared_task
from .models import TGUser


bot = Bot(token=settings.BOT_TOKEN)

BATCH_SIZE = 25
DELAY_BETWEEN_BATCHES = 1.5


@shared_task
def send_discount_reminders_task():
    inactive_users = TGUser.objects.filter(
        last_activity__lte=now() - timedelta(seconds=5),
        has_purchased=False
    ).values_list("tg_user_id", flat=True)

    if inactive_users:
        asyncio.run(_send_messages(inactive_users))


async def _send_messages(user_ids):
    """ Отправляет сообщения группами, предотвращая блокировку API.
    """
    async with bot.session:
        for i in range(0, len(user_ids), BATCH_SIZE):
            batch = user_ids[i:i + BATCH_SIZE]
            tasks = [_send_message(user_id) for user_id in batch]
            await asyncio.gather(*tasks)
            await asyncio.sleep(DELAY_BETWEEN_BATCHES)

async def _send_message(user_id):
    """ Отправляет сообщение пользователю и обрабатывает ошибки.
    """
    try:
        await bot.send_message(user_id, "Вы забыли оформить покупку! Вот ваша скидка 10%: ...")
    except TelegramAPIError as e:
        print(f"Ошибка при отправке {user_id}: {e}")