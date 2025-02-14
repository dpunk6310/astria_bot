from ninja import Router
from django.db.utils import IntegrityError
from loguru import logger as log

from telegram_api.api import send_message_successfully_pay
from config.settings import BOT_TOKEN
from dto.user import CreateUserDTO, UserDTO, UpdateUserDTO
from dto.image import CreateImageDTO, ImageDTO
from dto.payment import PaymentDTO, CreatePaymentDTO
from dto.tune import TuneListDTO, CreateTuneDTO
from dto.err import ErrorDTO, SuccessDTO
from dto.category import CategoryDTO
from dto.price_list import PriceListDTO
from asgiref.sync import sync_to_async
from .models import TGUser, Image, Payment, Tune, PriceList, Category


router = Router()


@router.get("/healthcheck")
async def healthcheck(request):
    return {"msg": "Ok Ok"}


@router.post("/create", response={201: UserDTO, 400: ErrorDTO})
async def create_user(request, create_user: CreateUserDTO):
    try:
        cln = await TGUser.objects.acreate(**create_user.dict())
    except IntegrityError as err:
        return 400, {"message": "error", "err": "such a tg user already exists"}
    return 201, cln


@router.post("/create-payment", response={201: PaymentDTO, 400: ErrorDTO})
async def create_payment(request, cr_pay: CreatePaymentDTO):
    try:
        payment = await Payment.objects.acreate(**cr_pay.dict())
        return 201, payment
    except Exception as err:
        return 400, {"message": "error", "err": str(err)}
    
    
@router.get("/get-payment/{payment_id}", response={200: PaymentDTO, 400: ErrorDTO})
async def get_payment(request, payment_id: str):
    try:
        payment = await Payment.objects.aget(payment_id=payment_id)
        return 200, payment
    except Exception as err:
        return 400, {"message": "error", "err": str(err)}


@router.post("/payment", response={200: SuccessDTO, 400: ErrorDTO})
async def payment_received(request):
    try:
        raw_body = request.body.decode("utf-8", errors="ignore")
        content_type = request.headers.get("Content-Type", "Unknown")
        # log.debug(f"Content-Type: {content_type}")
        # log.debug(f"Raw body: {raw_body}")
        data = request.POST.dict()
        
        payment = await Payment.objects.aget(payment_id=data["inv_id"])
        if payment.status:
            return 200, {"status": "ok", "message": "Success"}
        payment.status = True
        payment.save()
        
        callback_data = "driving"
        button_text = "Поехали!"
        
        tg_user: TGUser = await TGUser.objects.aget(
            tg_user_id=payment.tg_user_id,
        )
        if payment.is_first_payment:
            callback_data = "start_upload_photo"
            button_text = "Инструкция"
        if payment.is_first_payment is False and payment.learn_model:
            callback_data = "start_upload_photo"
            button_text = "Инструкция"
        
        tg_user.count_generations += payment.сount_generations
        tg_user.is_learn_model = True if payment.learn_model else False
        tg_user.save()
        
        result = send_message_successfully_pay(BOT_TOKEN, payment.tg_user_id, callback_data, button_text)

        return 200, {"status": "ok", "message": "Success"}
    except Payment.DoesNotExist as err:
        return 400, {"message": "error", "err": "payment not found"}
    except TGUser.DoesNotExist as err:
        return 400, {"message": "error", "err": "user not found"}


@router.get("/get-avatar-price-list", response={200: PriceListDTO, 400: ErrorDTO})
async def get_avatar_pay(request):
    try:
        price_list = await PriceList.objects.aget(learn_model=True)
    except Exception as err:
        return 400, {"message": "error", "err": "not price_list in db"}
    return 200, price_list


@router.get("/get-user/{tg_user_id}", response={200: UserDTO, 400: ErrorDTO})
async def get_user(request, tg_user_id: str):
    try:
        cln = await TGUser.objects.aget(tg_user_id=tg_user_id)
    except Exception as err:
        return 400, {"message": "error", "err": "not user in db"}
    return 200, cln


@router.get("/get-tunes/{tg_user_id}", response={200: list[TuneListDTO], 400: ErrorDTO})
async def get_tunes(request, tg_user_id: str):
    try:
        tunes = await sync_to_async(list)(Tune.objects.filter(tg_user_id=tg_user_id))
        if not tunes:
            return 400, {"message": "error", "err": "not tunes in db"}
        return 200, [TuneListDTO.model_validate(tune) for tune in tunes]
    except Exception as err:
        return 400, {"message": "error", "err": str(err)}


@router.get("/get-tune/{tune_id}", response={200: CreateTuneDTO, 400: ErrorDTO})
async def get_tune(request, tune_id: str):
    try:
        tune = await Tune.objects.aget(tune_id=tune_id)
    except Exception as err:
        return 400, {"message": "error", "err": "not tune in db"}
    return 200, tune


@router.get("/get-prices-list", response={200: list[PriceListDTO], 400: ErrorDTO})
async def get_price_list(request):
    try:
        price_list = await sync_to_async(list)(PriceList.objects.all().order_by("count"))
        return 200, [PriceListDTO.model_validate(price) for price in price_list]
    except Exception as err:
        return 400, {"message": "error", "err": "not price_list in db"}


@router.post("/create-tune", response={201: CreateTuneDTO, 400: ErrorDTO})
async def create_tune(request, req: CreateTuneDTO):
    try:
        tune = await Tune.objects.acreate(**req.dict())
    except Exception as err:
        return 400, {"message": "error", "err": "not tunes in db"}
    return 201, tune


@router.post("/update-user")
async def update_user(request, req: UpdateUserDTO):    
    try:
        updates = {k: v for k, v in req.dict().items() if v is not None}
        if updates:
            updated_rows = await TGUser.objects.filter(tg_user_id=req.tg_user_id).aupdate(**updates)
            if updated_rows == 0:
                return {"message": "error", "err": "User not found"}
        return {"status": "success"}
    except Exception as err:
        return {"message": "error", "err": str(err)}


@router.post("/create-img-path", response={201: ImageDTO, 400: ErrorDTO})
async def create_img_path(request, create_image: CreateImageDTO):
    try:
        user = await TGUser.objects.aget(tg_user_id=create_image.image.tg_user_id)
        images = Image.objects.filter(tg_user=user)
        if images.count() >= 10:
            images.delete()
        
        cln = await Image.objects.acreate(
            tg_user=user,
            img_path=create_image.image.path,
        )
    except TGUser.DoesNotExist:
        return 400, {"message": "error", "err": "User not found"}
    except Exception as err:
        return 400, {"message": "error", "err": str(err)}
    
    return 201, ImageDTO(path=cln.img_path, tg_user_id=cln.tg_user.tg_user_id)


@router.get("/user-images/{tg_user_id}", response={200: list[ImageDTO], 400: ErrorDTO})
async def get_user_images(request, tg_user_id: str):
    try:
        tg_user = await TGUser.objects.aget(tg_user_id=tg_user_id)
        images = await sync_to_async(list)(Image.objects.filter(tg_user=tg_user))
        return 200, [ImageDTO(path=image.img_path, tg_user_id=image.tg_user.tg_user_id) for image in images]
    except TGUser.DoesNotExist:
        return 400, {"message": "error", "err": "User not found"}
    except Exception as err:
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
    
    
@router.delete("/delete-user-images/{tg_user_id}", response={200: dict, 400: ErrorDTO, 404: ErrorDTO})
async def delete_user_images(request, tg_user_id: str):
    try:
        user = await TGUser.objects.aget(tg_user_id=tg_user_id)
        
        deleted_count, _ = await Image.objects.filter(tg_user=user).adelete()
        
        if deleted_count == 0:
            return 404, {"message": "error", "err": "No images found for this user."}
        
        return 200, {"message": "error", "err": f"Deleted {deleted_count} images successfully."}

    except TGUser.DoesNotExist:
        return 404, {"message": "error", "err": "User not found"}
    except Exception as err:
        return 400, {"message": "Error deleting images", "err": str(err)}
