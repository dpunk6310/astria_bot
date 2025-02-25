import json
import random
import time
from datetime import timedelta
from pathlib import Path

import asyncio
from asgiref.sync import async_to_sync, sync_to_async
from loguru import logger as log
from aiogram.exceptions import TelegramAPIError
from aiogram import Bot
from django.conf import settings
from django.utils.timezone import now
from django.core.paginator import Paginator
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from django.db.utils import IntegrityError

from .robo import generate_payment_link
from celery import shared_task
from .models import TGUser, Newsletter, Payment, Category, Promt


bot = Bot(token=settings.BOT_TOKEN)

BATCH_SIZE = 50
DELAY_BETWEEN_BATCHES = 1
BASE_DIR = Path(__file__).resolve().parent.parent



@shared_task
def send_discount_reminders_task(amount: int | float, сount_generations: int = 10, count_video_generations: int = 0):
    newsletters = Newsletter.objects.filter(squeeze=True)
    
    for newsletter in newsletters:
        inactive_users = TGUser.objects.filter(
            last_activity__lte=now() - timedelta(seconds=newsletter.delay_hours),
            has_purchased=False
        ).exclude(sent_messages__contains=newsletter.id)
        log.debug(f"Пользователей для рассылки: {len(inactive_users)}")
        user_ids = list(inactive_users.values_list("tg_user_id", flat=True))
            
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Купить!",
            callback_data=f"reminders_{amount}_{сount_generations}_{count_video_generations}"
        )
        if user_ids:
            async_to_sync(_send_messages_reminders)(user_ids, newsletter.message_text, builder.as_markup())
            
        for user in inactive_users:
            user.sent_messages.append(newsletter.id)
            user.save(update_fields=["sent_messages"])


@shared_task
def send_newsletters_task(slug: str):

    newsletter = Newsletter.objects.get(slug=slug)
    users_ids = TGUser.objects.values_list("tg_user_id", flat=True)
    paginator = Paginator(users_ids, 500)

    for page_number in paginator.page_range:
        page = paginator.page(page_number)
        user_ids_batch = list(page.object_list)
        async_to_sync(_send_messages_newsletters)(user_ids_batch, newsletter.message_text)


async def _send_messages_reminders(user_ids: list[int], text: str, reply_markup: types.InlineKeyboardMarkup):
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
                if reply_markup:
                    tasks.append(_send_message(user_id, text, reply_markup))
            await asyncio.gather(*tasks)
            await asyncio.sleep(DELAY_BETWEEN_BATCHES)
            
            
async def _send_messages_newsletters(user_ids: list[int], text: str):
    async with bot.session:
        for i in range(0, len(user_ids), BATCH_SIZE):
            batch = user_ids[i:i + BATCH_SIZE]
            tasks = []
            for user_id in batch:
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
        user = await sync_to_async(TGUser.objects.get)(tg_user_id=user_id)
        await sync_to_async(user.delete)()


@shared_task
def import_promts_from_json():
    
    json_file_path = BASE_DIR / "media" / "promts.json"
    
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for gender, categories in data.items():
        for category_data in categories['categories']:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                # slug=slugify(category_data['name']),
                gender=gender
            )

            for promt_text in category_data['promts']:
                try:
                    Promt.objects.create(
                        category=category,
                        text=promt_text
                    )
                except IntegrityError as err:
                    log.error(err)
                    continue
                
