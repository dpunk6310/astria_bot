import json
from datetime import timedelta
from pathlib import Path

from asgiref.sync import async_to_sync
from loguru import logger as log
from django.utils.timezone import now
from django.core.paginator import Paginator
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum, Count, F
from django.db.models.functions import Cast
from django.db.models import DecimalField
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.db.utils import IntegrityError
from celery import shared_task

from .models import TGUser, Newsletter, Category, Promt, Payment
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
    
    users_to_update = []
    for user in inactive_users:
        if newsletter.id not in user.sent_messages:
            user.sent_messages.append(newsletter.id)
            users_to_update.append(user)
    
    # Массовое обновление
    TGUser.objects.bulk_update(users_to_update, ['sent_messages'])


@shared_task
def send_newsletters_task(slug: str):
    """ Таска для рассылки сообщений пользователям
    """
    newsletter = Newsletter.objects.get(slug=slug)
    users_ids = TGUser.objects.values_list("tg_user_id", flat=True).order_by('id')
    paginator = Paginator(users_ids, 500)

    for page_number in paginator.page_range:
        page = paginator.page(page_number)
        user_ids_batch = list(page.object_list)
        photo_url = None
        if newsletter.photo:
            photo_url = newsletter.photo.path
        async_to_sync(send_messages_newsletters)(user_ids_batch, newsletter.message_text, photo_url)


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


@shared_task
def update_referral_statistics():
    """ Обновляет статистику рефералов и начисляет бонусы за успешные платежи.
    """
    # Находим всех пользователей с рефералами
    users_with_referrals = TGUser.objects.exclude(referal=None)

    # Собираем список всех рефереров
    master_refs = [user.referal for user in users_with_referrals]

    # Обнуляем статистику у всех рефереров
    TGUser.objects.filter(tg_user_id__in=master_refs).update(
        reward_generations=0,
        referral_purchases=0,
        referral_count=0,
        referral_purchases_amount=0.0  # Обнуляем сумму платежей
    )

    # Находим все успешные первые платежи рефералов
    successful_payments = Payment.objects.filter(
        tg_user_id__in=[user.tg_user_id for user in users_with_referrals],
        status=True,
        is_first_payment=True
    )

    # Словарь для хранения данных о рефералах
    referral_data = {}

    # Обрабатываем каждый успешный платеж
    for payment in successful_payments:
        tg_user_id = payment.tg_user_id
        referal_user = TGUser.objects.filter(tg_user_id=tg_user_id).first()

        if referal_user and referal_user.referal:
            referal_id = referal_user.referal

            # Инициализируем данные, если реферер еще не в словаре
            if referal_id not in referral_data:
                referral_data[referal_id] = {
                    'reward_generations': 0,
                    'referral_purchases': 0,
                    'referral_purchases_amount': 0.0
                }

            # Начисляем бонусы и считаем платежи
            referral_data[referal_id]['reward_generations'] += 20
            referral_data[referal_id]['referral_purchases'] += 1
            referral_data[referal_id]['referral_purchases_amount'] += float(payment.amount)

    # Считаем количество рефералов для каждого реферера
    referral_counts = (
        TGUser.objects.filter(referal__in=master_refs)
        .values('referal')
        .annotate(referral_count=Count('id'))
    )
    referral_counts_dict = {item['referal']: item['referral_count'] for item in referral_counts}

    # Подготавливаем пользователей для обновления
    users_to_update = []
    for referal_id, data in referral_data.items():
        referal_user = TGUser.objects.filter(tg_user_id=referal_id).first()
        if referal_user:
            referal_user.reward_generations = data['reward_generations']
            referal_user.referral_purchases = data['referral_purchases']
            referal_user.referral_count = referral_counts_dict.get(referal_id, 0)
            referal_user.referral_purchases_amount = data['referral_purchases_amount']
            users_to_update.append(referal_user)

    # Массовое обновление пользователей
    TGUser.objects.bulk_update(
        users_to_update,
        ['reward_generations', 'referral_purchases', 'referral_count', 'referral_purchases_amount']
    )
    

@shared_task
def update_user_purchases_task():
    users = TGUser.objects.all().order_by('id')
    paginator = Paginator(users, 500)
    total_processed = 0

    for page_number in paginator.page_range:
        page = paginator.page(page_number)
        for user in page.object_list.iterator():
            user_purchases = Payment.objects.filter(
                tg_user_id=user.tg_user_id,
                status=True
            ).annotate(
                amount_as_decimal=Cast('amount', output_field=DecimalField(max_digits=10, decimal_places=2))
            ).aggregate(
                total_count=Count('id'),
                total_amount=Sum('amount_as_decimal')
            )

            user.user_purchases_count = user_purchases['total_count'] or 0
            user.user_purchases_amount = float(user_purchases['total_amount'] or 0)
            user.save()
            total_processed += 1
                
    return total_processed


# @shared_task
# def debiting_money_for_subscription_task(days: Optional[int]):
#     now = timezone.now()
#     today = now.date()
#     notify_date = now + timedelta(days=days)
    
#     users_to_notify_days = TGUser.objects.filter(subscribe__lte=notify_date, subscribe__gt=now)
#     users_to_notify = TGUser.objects.filter(subscribe__date=today)
#     for user in users_to_notify:
#         # Отправляем уведомление пользователю
#         message = f"Ваша подписка заканчивается сегодня ({user.subscribe.strftime('%Y-%m-%d')}). Продлите подписку, чтобы продолжить пользоваться услугами."
#         send_message(user.tg_user_id, message)
                
