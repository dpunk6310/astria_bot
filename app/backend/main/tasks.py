from datetime import timedelta

from loguru import logger as log
from aiogram.exceptions import TelegramAPIError
from aiogram import Bot
from django.conf import settings
from django.utils.timezone import now

from config import celery_app
from .models import TGUser


@celery_app.task(
    name="main.tasks.send_discount_reminders_task",
)
def send_discount_reminders_task():
    inactive_users = TGUser.objects.filter(
        last_activity__lte=now() - timedelta(hours=6),
        has_purchased=False
    ).values_list("tg_user_id", flat=True)
    log.debug(len(inactive_users))
    log.debug(inactive_users)


# @shared_task
# def send_discount_reminders():
#     """Отправляет напоминания пользователям, которые не сделали покупку."""
    
#     # Получаем только нужные данные (telegram_id)
#     inactive_users = User.objects.filter(
#         last_activity__lte=now() - timedelta(hours=6),
#         has_purchased=False
#     ).values_list("telegram_id", flat=True)

#     if inactive_users:
#         asyncio.run(_send_messages(inactive_users))

# async def _send_messages(user_ids):
#     """Асинхронно отправляет сообщения всем пользователям."""
#     tasks = []
#     async with bot.session:
#         for user_id in user_ids:
#             tasks.append(_send_message(user_id))
#         await asyncio.gather(*tasks)

# async def _send_message(user_id):
#     """Отправляет сообщение пользователю и обрабатывает возможные ошибки."""
#     try:
#         await bot.send_message(user_id, "Вы забыли оформить покупку! Вот ваша скидка 10%: ...")
#     except TelegramAPIError as e:
#         print(f"Ошибка при отправке сообщения {user_id}: {e}")
