from datetime import datetime, timedelta
import random
import json

from ninja import Router
from django.db.utils import IntegrityError
from loguru import logger as log
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from telegram_api.api import send_message_successfully_pay, send_promo_message
from config.settings import BOT_TOKEN
from dto.user import CreateUserDTO, UserDTO, UpdateUserDTO
from dto.payment import PaymentDTO, CreatePaymentDTO
from dto.tune import TuneListDTO, CreateTuneDTO
from dto.err import ErrorDTO, SuccessDTO
from dto.category import CategoryDTO
from dto.promo import UpdatePromoDTO
from dto.price_list import PriceListDTO
from dto.tgimage import TGImageDTO, CreateTGImageDTO
from .models import (
    TGUser, 
    Payment, 
    Tune, 
    PriceList, 
    Category, 
    TGImage,
    Promocode,
)
from .utils import generate_promo_code


router = Router()


@router.get("/healthcheck")
async def healthcheck(request):
    return {"msg": "Ok Ok"}


@router.post("/create", response={201: UserDTO, 400: ErrorDTO})
async def create_user(request, create_user: CreateUserDTO):
    try:
        cln = await sync_to_async(TGUser.objects.create)(**create_user.dict())
        return 201, cln
    except IntegrityError as err:
        return 400, {"message": "error", "err": "such a tg user already exists"}
    except Exception as err:
        return 400, {"message": "error", "err": str(err)}


@router.post("/create-payment", response={201: PaymentDTO, 400: ErrorDTO})
async def create_payment(request, cr_pay: CreatePaymentDTO):
    try:
        payment = await sync_to_async(Payment.objects.create)(**cr_pay.dict())
        return 201, payment
    except Exception as err:
        return 400, {"message": "error", "err": str(err)}


@router.get("/get-payment/{payment_id}", response={200: PaymentDTO, 400: ErrorDTO})
async def get_payment(request, payment_id: str):
    try:
        payment = await sync_to_async(Payment.objects.get)(payment_id=payment_id)
        return 200, payment
    except ObjectDoesNotExist:
        return 400, {"message": "error", "err": "Payment not found"}
    except Exception as err:
        return 400, {"message": "error", "err": str(err)}


@router.post("/payment", response={200: SuccessDTO, 400: ErrorDTO})
async def payment_received(request):
    try:
        raw_body = request.body.decode("utf-8", errors="ignore")
        content_type = request.headers.get("Content-Type", "Unknown")
        data = request.POST.dict()
        log.debug(data)
        payment = await sync_to_async(Payment.objects.get)(payment_id=data["inv_id"])
        if payment.status:
            return 200, {"status": "ok", "message": "Success"}
        payment.status = True
        await sync_to_async(payment.save)()

        callback_data = "driving"
        button_text = "Поехали!"

        tg_user = await sync_to_async(TGUser.objects.get)(tg_user_id=payment.tg_user_id)
        
        # Первый платеж
        if payment.is_first_payment:
            callback_data = "start_upload_photo"
            button_text = "Инструкция"
            tg_user.maternity_payment_id = payment.payment_id
            tg_user.subscribe = datetime.now() + timedelta(days=30)
            try:
                if tg_user.referal and tg_user.referal != "":
                    referal = await sync_to_async(TGUser.objects.get)(tg_user_id=tg_user.referal)
                    referal.count_generations += 20
                    await sync_to_async(referal.save)()
            except Exception as err:
                log.error(err)
            tg_user.count_generations += payment.сount_generations
            tg_user.count_video_generations += payment.count_video_generations
            tg_user.has_purchased = True
            await sync_to_async(tg_user.save)()
            result = send_message_successfully_pay(BOT_TOKEN, payment.tg_user_id, callback_data, button_text)
            return 200, {"status": "ok", "message": "Success"}
        
        # Продление подписки
        if payment.subscription_renewal:
            tg_user.subscribe = datetime.now() + timedelta(days=30)
            tg_user.attempt = 0
            tg_user.is_learn_model = bool(payment.learn_model)
            tg_user.count_generations += payment.сount_generations
            tg_user.count_video_generations += payment.count_video_generations
            tg_user.has_purchased = True
            await sync_to_async(tg_user.save)()
            return 200, {"status": "ok", "message": "Success"}
        
        # Оплата обучения
        if not payment.is_first_payment and not payment.subscription_renewal and payment.learn_model and not payment.promo:
            callback_data = "start_upload_photo"
            button_text = "Инструкция"
            tg_user.is_learn_model = bool(payment.learn_model)
            result = send_message_successfully_pay(BOT_TOKEN, payment.tg_user_id, callback_data, button_text)
            await sync_to_async(tg_user.save)()
            return 200, {"status": "ok", "message": "Success"}
            
        # Покупка промокода
        if payment.promo is True:
            promocode_gen = generate_promo_code(10)
            log.debug(promocode_gen)
            try:
                promo = await sync_to_async(Promocode.objects.get)(code=promocode_gen) 
            except ObjectDoesNotExist:
                promo = await sync_to_async(Promocode.objects.create)(
                    tg_user_id=tg_user.tg_user_id,
                    code=promocode_gen,
                    count_generations=payment.count_generations_for_gift,
                    count_video_generations=payment.count_generations_video_for_gift,
                    is_learn_model=payment.learn_model,
                )
            log.debug(promo)
            result = send_promo_message(BOT_TOKEN, payment.tg_user_id, promocode_gen)
            log.debug(result)
            return 200, {"status": "ok", "message": "Success"}

        tg_user.count_generations += payment.сount_generations
        tg_user.count_video_generations += payment.count_video_generations
        tg_user.has_purchased = True
        await sync_to_async(tg_user.save)()
        
        result = send_message_successfully_pay(BOT_TOKEN, payment.tg_user_id, callback_data, button_text)

        return 200, {"status": "ok", "message": "Success"}
    except ObjectDoesNotExist as err:
        log.error(err)
        return 400, {"message": "error", "err": "Payment or user not found"}
    except Exception as err:
        log.error(err)
        return 400, {"message": "error", "err": str(err)}


@router.get("/get-avatar-price-list", response={200: PriceListDTO, 400: ErrorDTO})
async def get_avatar_pay(request):
    try:
        price_list = await sync_to_async(PriceList.objects.filter(learn_model=True).exclude(type_price_list="promo").first)()
        if not price_list:
            return 400, {"message": "error", "err": "Price list not found"}
        return 200, price_list
    except ObjectDoesNotExist:
        return 400, {"message": "error", "err": "Price list not found"}
    except Exception as err:
        return 400, {"message": "error", "err": str(err)}


@router.get("/get-user/{tg_user_id}", response={200: UserDTO, 400: ErrorDTO})
async def get_user(request, tg_user_id: str):
    try:
        cln = await sync_to_async(TGUser.objects.get)(tg_user_id=tg_user_id)
        return 200, cln
    except Exception as err:
        log.error(err)
        return 400, {"message": "error", "err": str(err)}


@router.get("/get-tunes/{tg_user_id}", response={200: list[TuneListDTO], 400: ErrorDTO})
async def get_tunes(request, tg_user_id: str):
    try:
        tunes = await sync_to_async(list)(Tune.objects.filter(tg_user_id=tg_user_id))
        if not tunes:
            return 400, {"message": "error", "err": "No tunes found"}
        return 200, [TuneListDTO.model_validate(tune) for tune in tunes]
    except Exception as err:
        return 400, {"message": "error", "err": str(err)}


@router.get("/get-tune/{tune_id}", response={200: CreateTuneDTO, 400: ErrorDTO})
async def get_tune(request, tune_id: str):
    try:
        tune = await sync_to_async(Tune.objects.get)(tune_id=tune_id)
        return 200, tune
    except ObjectDoesNotExist:
        return 400, {"message": "error", "err": "Tune not found"}
    except Exception as err:
        return 400, {"message": "error", "err": str(err)}


@router.get("/get-prices-list/{type_price_list}", response={200: list[PriceListDTO], 400: ErrorDTO})
async def get_price_list(request, type_price_list: str):
    try:
        price_list = await sync_to_async(list)(PriceList.objects.filter(
            type_price_list=type_price_list,
        ).order_by("count"))
        return 200, [PriceListDTO.model_validate(price) for price in price_list]
    except Exception as err:
        return 400, {"message": "error", "err": str(err)}


@router.post("/create-tune", response={201: CreateTuneDTO, 400: ErrorDTO})
async def create_tune(request, req: CreateTuneDTO):
    try:
        tune = await sync_to_async(Tune.objects.create)(**req.dict())
        return 201, tune
    except Exception as err:
        return 400, {"message": "error", "err": str(err)}


@router.post("/update-user")
async def update_user(request, req: UpdateUserDTO):
    
    try:
        updates = req.dict()
        tg_user_id = updates.pop("tg_user_id")
        request_data = json.loads(request.body.decode("utf-8"))
        updates = {k: v for k, v in updates.items() if k in request_data}
        
        log.debug(f"Updates to apply: {updates}")
        updated_rows = await sync_to_async(TGUser.objects.filter(tg_user_id=tg_user_id).update)(**updates)
        
        if updated_rows == 0:
            log.warning(f"User not found: tg_user_id={tg_user_id}")
            return {"message": "error", "err": "User not found"}
        
        log.info(f"User updated: tg_user_id={tg_user_id}, updates={updates}")
        return {"status": "success"}
    except Exception as err:
        log.error(f"Error updating user: {err}")
        return {"message": "error", "err": str(err)}
    
    
@router.post("/update-promo")
async def update_promo(request, req: UpdatePromoDTO):
    try:
        code = req.code
        tg_user_id = req.tg_user_id
        new_status = req.status

        promocode = await sync_to_async(Promocode.objects.filter(code=code).first)()
        
        if not promocode:
            log.warning(f"Promocode not found: code={code}")
            return {"message": "error", "err": "Promocode not found"}
        if promocode.status:
            promocode.status = new_status
            promocode.tg_user_id = tg_user_id
            await sync_to_async(promocode.save)()
            
            user = await sync_to_async(TGUser.objects.filter(tg_user_id=tg_user_id).first)()
            if not user:
                log.warning(f"User not found: tg_user_id={tg_user_id}")
                return {"message": "error", "err": "User not found"}
            
            user.count_generations += promocode.count_generations
            user.count_video_generations += promocode.count_video_generations
            if not user.is_learn_model:
                user.is_learn_model = promocode.is_learn_model
            await sync_to_async(user.save)()
            
            log.info(f"Promocode updated: code={code}, tg_user_id={tg_user_id}, status={new_status}")
            return {
                "code": promocode.code,
                "status": promocode.status,
                "count_generations": promocode.count_generations,
                "count_video_generations": promocode.count_video_generations,
                "is_learn_model": promocode.is_learn_model,
            }
        return {"status": "unactive"}
    except Exception as err:
        log.error(f"Error updating promocode: {err}")
        return {"message": "error", "err": str(err)}

    
@router.post("/create-tgimg", response={201: TGImageDTO, 400: ErrorDTO})
def create_tg_img(request, create_image: CreateTGImageDTO):
    try:
        user = TGUser.objects.get(tg_user_id=create_image.tg_user_id)
        
        cln, created = TGImage.objects.get_or_create(
            tg_user=user,
            img_hash=create_image.tg_hash,
        )
        
        return 201, TGImageDTO(tg_hash=cln.img_hash, tg_user_id=cln.tg_user.tg_user_id, id=cln.id)
    except ObjectDoesNotExist:
        return 400, {"message": "error", "err": "User not found"}
    except Exception as err:
        return 400, {"message": "error", "err": str(err)}
    
    
@router.get("/get-tgimg/{id}", response={200: TGImageDTO, 400: ErrorDTO})
def get_tg_img(request, id: int):
    try:
        cln = TGImage.objects.get(id=id)
        print(cln)
        return 200, TGImageDTO(
            id=cln.id,
            tg_hash=cln.img_hash,
            tg_user_id=cln.tg_user.tg_user_id
        )
    except ObjectDoesNotExist:
        return 400, {"message": "error", "err": "Image not found"}
    except Exception as err:
        print("ошибка тут ", err)
        return 400, {"message": "error", "err": str(err)}


@router.get("/categories/{gender}", response={200: list[CategoryDTO], 400: ErrorDTO})
async def get_categories(request, gender: str):
    try:
        categories = await sync_to_async(list)(Category.objects.filter(gender=gender).prefetch_related("promts"))
        category_list = [
            {
                "name": category.name,
                "slug": category.slug,
                "gender": category.gender,
                "promts": await sync_to_async(list)(category.promts.values("text"))
            }
            for category in categories
        ]
        return 200, category_list
    except Exception as err:
        return 400, {"message": "error", "err": str(err)}
    
    
@router.get("/random-prompt/{category_slug}", response={200: str, 400: dict, 404: dict})
async def get_random_prompt(request, category_slug: str):
    try:
        # Получаем категорию, если не найдена — автоматически 404
        category = await sync_to_async(get_object_or_404, thread_sensitive=True)(Category, slug=category_slug)

        # Получаем список промтов
        prompts = await sync_to_async(list, thread_sensitive=True)(category.promts.values_list("text", flat=True))

        if not prompts:
            return 400, {"message": "error", "err": "No prompts found in this category"}

        return 200, random.choice(prompts)
    except Exception as err:
        return 400, {"message": "error", "err": str(err)}
