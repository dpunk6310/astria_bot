import json
import random
from datetime import timedelta, date
from pathlib import Path

from asgiref.sync import async_to_sync
from loguru import logger as log
from django.conf import settings
from django.utils.timezone import now
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from django.db.models.functions import Cast
from django.db.models import DecimalField
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.db.utils import IntegrityError
from celery import shared_task

from telegram_api.api import send_message_successfully_pay, send_promo_message
from config.settings import BOT_TOKEN

from .models import (
    Promocode,
    TGUser, 
    Newsletter, 
    Category, 
    Promt, 
    Payment,
    PriceList,
    Tune
)
from .utils import generate_promo_code, send_messages_newsletters, send_messages_reminders
from .robo import create_recurring_payment


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


@shared_task
def recurring_payment_task(robo_pay: bool = False, attempt: int = 5):
    users = TGUser.objects.filter(subscribe__lte=date.today(), maternity_payment_id__isnull=False, attempt__lte=5)
    log.debug(users)
    for user in users:
        if user.attempt == attempt:
            user.subscribe = None
            user.maternity_payment_id = None
            user.attempt = 0
            user.save()
            continue
        payment = Payment.objects.filter(payment_id=user.maternity_payment_id).first()
        if not payment:
            continue 
        while True:
            payment_id = random.randint(10, 214748347)
            if not Payment.objects.filter(payment_id=str(payment_id)).exists():
                cr_payment_id = str(payment_id)
                break

        amount = int(payment.amount)

        new_payment = Payment.objects.create(
            tg_user_id=user.tg_user_id,
            payment_id=cr_payment_id,
            status=False,
            сount_generations=payment.сount_generations,
            count_video_generations=payment.count_video_generations,
            amount=amount,
            learn_model=bool(payment.learn_model),
            is_first_payment=False,
            subscription_renewal=True,
        )

        try:
            if robo_pay:
                response = create_recurring_payment(
                    merchant_login=settings.ROBOKASSA_MERCHANT_ID,
                    merchant_password_1=settings.ROBOKASSA_PASSWORD1,
                    invoice_id=int(new_payment.payment_id),
                    previous_invoice_id=payment.payment_id,
                    robokassa_recurring_url="https://auth.robokassa.ru/Merchant/Recurring",
                    tg_user_id=user.tg_user_id,
                    amount=amount
                )

                log.debug(f"Создан дочерний платеж для пользователя {user.tg_user_id}. Payment ID: {new_payment.payment_id}")

        except Exception as e:
            log.error(f"Ошибка при создании дочернего платежа для пользователя {user.tg_user_id}: {e}")
        user.attempt += 1
        user.save()

        log.debug(f"Пользователь {user.tg_user_id}. Текущее количество попыток: {user.attempt}")


@shared_task
def create_default_price_list():
    PriceList.objects.all().delete()
    PriceList.objects.create(
        price=499,
        count=1,
        learn_model=True,
        sale=None,
        type_price_list=None
    )
    PriceList.objects.create(
        price=300,
        count=10,
        learn_model=False,
        sale=None,
        type_price_list="photo"
    )
    PriceList.objects.create(
        price=999,
        count=50,
        learn_model=False,
        sale="-34%",
        type_price_list="photo"
    )
    PriceList.objects.create(
        price=1990,
        count=100,
        learn_model=False,
        sale="-38%",
        type_price_list="photo"
    )
    PriceList.objects.create(
        price=4990,
        count=300,
        learn_model=False,
        sale="-44%",
        type_price_list="photo"
    )
    PriceList.objects.create(
        price=7490,
        count=500,
        learn_model=False,
        sale="-50%",
        type_price_list="photo"
    )
    PriceList.objects.create(
        price=9990,
        count=1000,
        learn_model=False,
        sale="-66%",
        type_price_list="photo"
    )
    PriceList.objects.create(
        price=159,
        count=1,
        learn_model=False,
        sale=None,
        type_price_list="video"
    )
    PriceList.objects.create(
        price=590,
        count=5,
        learn_model=False,
        sale="-26%",
        type_price_list="video"
    )
    PriceList.objects.create(
        price=890,
        count=10,
        learn_model=False,
        sale="-44%",
        type_price_list="video"
    )
    PriceList.objects.create(
        price=3990,
        count=50,
        learn_model=False,
        sale="-50%",
        type_price_list="video"
    )
    # PriceList.objects.create(
    #     price=490,
    #     count=10,
    #     learn_model=True,
    #     sale=None,
    #     type_price_list="promo"
    # )


@shared_task
def update_tune_names_per_user():
    users = Tune.objects.values_list('tg_user_id', flat=True).distinct()
    
    for user_id in users:
        tunes = Tune.objects.filter(tg_user_id=user_id).exclude(name__isnull=False).order_by('id')
        for index, tune in enumerate(tunes, start=1):
            tune.name = f"Модель {index}"
        Tune.objects.bulk_update(tunes, ['name'])
