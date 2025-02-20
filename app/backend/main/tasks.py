import json
import random
from datetime import timedelta
from pathlib import Path

import asyncio
from asgiref.sync import async_to_sync
from loguru import logger as log
from aiogram.exceptions import TelegramAPIError
from aiogram import Bot
from django.conf import settings
from django.utils.timezone import now
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.core.exceptions import ObjectDoesNotExist

from .robo import generate_payment_link
from celery import shared_task
from .models import TGUser, Newsletter, Payment


bot = Bot(token=settings.BOT_TOKEN)

BATCH_SIZE = 50
DELAY_BETWEEN_BATCHES = 0.5
BASE_DIR = Path(__file__).resolve().parent.parent


@shared_task
def send_discount_reminders_task(amount: int | float, сount_generations: int = 10, count_video_generations: int = 0):
    """Основная таска Celery, которая запускает рассылку."""
    newsletters = Newsletter.objects.all()
    
    file_path = BASE_DIR / "media" / "payload.json"
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for newsletter in newsletters:
        inactive_users = TGUser.objects.filter(
            last_activity__lte=now() - timedelta(minutes=newsletter.delay_hours),
            has_purchased=False
        ).exclude(sent_messages__contains=newsletter.id)
        user_ids = list(inactive_users.values_list("tg_user_id", flat=True))
        
        payments = []
        for user_id in user_ids:
            while True:
                payment_id = random.randint(10, 214748347)
                try:
                    Payment.objects.get(payment_id=payment_id)
                except ObjectDoesNotExist:
                    break
            
            payment = Payment.objects.create(
                payment_id=payment_id,
                tg_user_id=user_id,  
                status=False,
                amount=str(amount),  
                learn_model=True,
                is_first_payment=True,
                сount_generations=сount_generations,
                count_video_generations=count_video_generations,
            )
            payments.append(payment)
        
        for i, v in enumerate(data):
            if v.get("Name") == "Первое предложение акции":
                index = i
                description = v.get("Name")
                break
        
        reply_markups = {}
        for payment in payments:
            payment_link = generate_payment_link(
                settings.ROBOKASSA_MERCHANT_ID,
                settings.ROBOKASSA_PASSWORD1,
                amount,
                int(payment.payment_id),
                description + f" {payment.tg_user_id}",
                items=[data[index]],
            )
            
            builder = InlineKeyboardBuilder()
            builder.button(
                text="Карта РФ",
                url=payment_link
            )
            builder.button(
                text="Зарубежная карта",
                url=payment_link
            )
            reply_markups[payment.tg_user_id] = builder.as_markup()
        
        if user_ids:
            async_to_sync(_send_messages_reminders)(user_ids, newsletter.message_text, reply_markups)
            
        for user in inactive_users:
            user.sent_messages.append(newsletter.id)
            user.save(update_fields=["sent_messages"])


async def _send_messages_reminders(user_ids: list[int], text: str, reply_markups: dict):
    """
    Асинхронно отправляет сообщения группами (batch), предотвращая блокировку API.
    :param user_ids: Список ID пользователей.
    :param text: Текст сообщения.
    :param reply_markups: Словарь с клавиатурами для каждого пользователя.
    """
    async with bot.session:
        for i in range(0, len(user_ids), BATCH_SIZE):
            batch = user_ids[i:i + BATCH_SIZE]
            tasks = []
            for user_id in batch:
                reply_markup = reply_markups.get(user_id)
                if reply_markup:
                    tasks.append(_send_message(user_id, text, reply_markup))
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
