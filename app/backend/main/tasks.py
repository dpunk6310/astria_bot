import json
from datetime import timedelta
from pathlib import Path

from asgiref.sync import async_to_sync
from loguru import logger as log
from django.utils.timezone import now
from django.core.paginator import Paginator
from django.db import transaction
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from django.db.utils import IntegrityError
from celery import shared_task

from .models import TGUser, Newsletter, Category, Promt
from .utils import send_messages_newsletters, send_messages_reminders


BASE_DIR = Path(__file__).resolve().parent.parent



@shared_task
def send_discount_reminders_task(slug: str, amount: int | float, сount_generations: int = 10, count_video_generations: int = 0):
    """ Таска для рассылки дожимки
    """
    newsletter = Newsletter.objects.get(slug=slug)
    
    inactive_users = TGUser.objects.filter(
        last_activity__lte=now() - timedelta(hours=newsletter.delay_hours),
        has_purchased=False
    ).exclude(sent_messages__contains=newsletter.id)
    
    log.debug(f"Пользователей для рассылки: {len(inactive_users)}")
    
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Купить!",
        callback_data=f"reminders_{amount}_{сount_generations}_{count_video_generations}"
    )
    
    user_ids = [user.tg_user_id for user in inactive_users]
    
    async_to_sync(send_messages_reminders)(user_ids, newsletter.message_text, builder.as_markup())
    
    with transaction.atomic():
        for user in inactive_users:
            user = TGUser.objects.select_for_update().get(tg_user_id=user.tg_user_id)
            if newsletter.id not in user.sent_messages:
                user.sent_messages.append(newsletter.id)
                user.save()


@shared_task
def send_newsletters_task(slug: str):
    """ Таска для рассылки сообщений пользователям
    """
    newsletter = Newsletter.objects.get(slug=slug)
    users_ids = TGUser.objects.values_list("tg_user_id", flat=True)
    paginator = Paginator(users_ids, 500)

    for page_number in paginator.page_range:
        page = paginator.page(page_number)
        user_ids_batch = list(page.object_list)
        async_to_sync(send_messages_newsletters)(user_ids_batch, newsletter.message_text)


@shared_task
def import_promts_from_json():
    """ Таска для импорта json файла с промтами в базу данных
    """
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
                
