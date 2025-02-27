from datetime import datetime, timedelta
import random

from ninja import Router
from django.db.utils import IntegrityError
from loguru import logger as log
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from telegram_api.api import send_message_successfully_pay
from config.settings import BOT_TOKEN
from dto.user import CreateUserDTO, UserDTO, UpdateUserDTO
from dto.image import CreateImageDTO, ImageDTO
from dto.payment import PaymentDTO, CreatePaymentDTO
from dto.tune import TuneListDTO, CreateTuneDTO
from dto.err import ErrorDTO, SuccessDTO
from dto.category import CategoryDTO
from dto.price_list import PriceListDTO
from .models import TGUser, Image, Payment, Tune, PriceList, Category


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

        payment = await sync_to_async(Payment.objects.get)(payment_id=data["inv_id"])
        if payment.status:
            return 200, {"status": "ok", "message": "Success"}
        payment.status = True
        await sync_to_async(payment.save)()

        callback_data = "driving"
        button_text = "Поехали!"

        tg_user = await sync_to_async(TGUser.objects.get)(tg_user_id=payment.tg_user_id)
        if payment.is_first_payment:
            callback_data = "start_upload_photo"
            button_text = "Инструкция"
            tg_user.maternity_payment_id = payment.payment_id
            tg_user.subscribe = datetime.now() + timedelta(days=30)
        if not payment.is_first_payment and payment.learn_model:
            callback_data = "start_upload_photo"
            button_text = "Инструкция"

        tg_user.count_generations += payment.сount_generations
        tg_user.is_learn_model = bool(payment.learn_model)
        tg_user.count_video_generations += payment.count_video_generations
        tg_user.has_purchased = True
        await sync_to_async(tg_user.save)()

        result = send_message_successfully_pay(BOT_TOKEN, payment.tg_user_id, callback_data, button_text)

        return 200, {"status": "ok", "message": "Success"}
    except ObjectDoesNotExist as err:
        return 400, {"message": "error", "err": "Payment or user not found"}
    except Exception as err:
        return 400, {"message": "error", "err": str(err)}


@router.get("/get-avatar-price-list", response={200: PriceListDTO, 400: ErrorDTO})
async def get_avatar_pay(request):
    try:
        price_list = await sync_to_async(PriceList.objects.get)(learn_model=True)
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
    except ObjectDoesNotExist:
        return 400, {"message": "error", "err": "User not found"}
    except Exception as err:
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
        updates = {k: v for k, v in req.dict().items() if v is not None}
        if updates:
            updated_rows = await sync_to_async(TGUser.objects.filter(tg_user_id=req.tg_user_id).update)(**updates)
            if updated_rows == 0:
                return {"message": "error", "err": "User not found"}
        return {"status": "success"}
    except Exception as err:
        return {"message": "error", "err": str(err)}


@router.post("/create-img-path", response={201: ImageDTO, 400: ErrorDTO})
async def create_img_path(request, create_image: CreateImageDTO):
    try:
        user = await sync_to_async(TGUser.objects.get)(tg_user_id=create_image.image.tg_user_id)
        images = await sync_to_async(Image.objects.filter)(tg_user=user)
        if await sync_to_async(images.count)() >= 10:
            await sync_to_async(images.delete)()
        cln = await sync_to_async(Image.objects.create)(
            tg_user=user,
            img_path=create_image.image.path,
        )
        return 201, ImageDTO(path=cln.img_path, tg_user_id=cln.tg_user.tg_user_id)
    except ObjectDoesNotExist:
        return 400, {"message": "error", "err": "User not found"}
    except Exception as err:
        return 400, {"message": "error", "err": str(err)}


@router.get("/user-images/{tg_user_id}", response={200: list[ImageDTO], 400: ErrorDTO})
def get_user_images(request, tg_user_id: str):
    try:
        tg_user = TGUser.objects.get(tg_user_id=tg_user_id)

        images = Image.objects.filter(tg_user=tg_user)

        image_dtos = [ImageDTO(path=image.img_path, tg_user_id=image.tg_user.tg_user_id) for image in images]

        return 200, image_dtos
    except Exception as err:
        print(err)
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


@router.delete("/delete-user-images/{tg_user_id}", response={200: dict, 400: ErrorDTO, 404: ErrorDTO})
async def delete_user_images(request, tg_user_id: str):
    try:
        user = await sync_to_async(TGUser.objects.get)(tg_user_id=tg_user_id)
        deleted_count = await sync_to_async(Image.objects.filter(tg_user=user).delete)()
        if deleted_count[0] == 0:
            return 404, {"message": "error", "err": "No images found for this user."}
        return 200, {"message": "success", "err": f"Deleted {deleted_count[0]} images successfully."}
    except ObjectDoesNotExist:
        return 404, {"message": "error", "err": "User not found"}
    except Exception as err:
        return 400, {"message": "error", "err": str(err)}