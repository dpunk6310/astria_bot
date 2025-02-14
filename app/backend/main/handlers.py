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
from .models import TGUser, Image, Payment, Tune, PriceList, Category


router = Router()


@router.get("/healthcheck")
def healthcheck(request):
    return {"msg": "Ok Ok"}


@router.post("/create", response={201: UserDTO, 400: ErrorDTO})
def create_user(request, create_user: CreateUserDTO):
    try:
        cln = TGUser.objects.create(**create_user.dict())
    except IntegrityError as err:
        return 400, {"message": "error", "err": "such a tg user already exists"}
    return 201, cln


@router.post("/create-payment", response={201: PaymentDTO, 400: ErrorDTO})
def create_payment(request, cr_pay: CreatePaymentDTO):
    try:
        payment = Payment.objects.create(**cr_pay.dict())
        return 201, payment
    except Exception as err:
        return 400, {"message": "error", "err": str(err)}
    
    
@router.get("/get-payment/{payment_id}", response={200: PaymentDTO, 400: ErrorDTO})
def get_payment(request, payment_id: str):
    try:
        payment = Payment.objects.get(payment_id=payment_id)
        return 200, payment
    except Exception as err:
        return 400, {"message": "error", "err": str(err)}


@router.post("/payment", response={200: SuccessDTO, 400: ErrorDTO})
def payment_received(request):
    try:
        raw_body = request.body.decode("utf-8", errors="ignore")
        content_type = request.headers.get("Content-Type", "Unknown")
        # log.debug(f"Content-Type: {content_type}")
        # log.debug(f"Raw body: {raw_body}")
        data = request.POST.dict()
        
        payment = Payment.objects.get(payment_id=data["inv_id"])
        if payment.status:
            return 200, {"status": "ok", "message": "Success"}
        payment.status = True
        payment.save()
        
        callback_data = "driving"
        button_text = "Поехали!"
        
        tg_user: TGUser = TGUser.objects.get(
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
def get_avatar_pay(request):
    try:
        price_list = PriceList.objects.get(learn_model=True)
    except Exception as err:
        return 400, {"message": "error", "err": "not price_list in db"}
    return 200, price_list


@router.get("/get-user/{tg_user_id}", response={200: UserDTO, 400: ErrorDTO})
def get_user(request, tg_user_id: str):
    try:
        cln = TGUser.objects.get(tg_user_id=tg_user_id)
    except Exception as err:
        return 400, {"message": "error", "err": "not user in db"}
    return 200, cln


@router.get("/get-tunes/{tg_user_id}", response={200: list[TuneListDTO], 400: ErrorDTO})
def get_tunes(request, tg_user_id: str):
    try:
        tunes = Tune.objects.filter(tg_user_id=tg_user_id)
    except Exception as err:
        return 400, {"message": "error", "err": "not tunes in db"}
    return 200, tunes


@router.get("/get-tune/{tune_id}", response={200: CreateTuneDTO, 400: ErrorDTO})
def get_tune(request, tune_id: str):
    try:
        tune = Tune.objects.get(tune_id=tune_id)
    except Exception as err:
        return 400, {"message": "error", "err": "not tune in db"}
    return 200, tune


@router.get("/get-prices-list", response={200: list[PriceListDTO], 400: ErrorDTO})
def get_price_list(request):
    try:
        price_list = PriceList.objects.all().order_by("count")
    except Exception as err:
        return 400, {"message": "error", "err": "not price_list in db"}
    return 200, price_list


@router.post("/create-tune", response={201: CreateTuneDTO, 400: ErrorDTO})
def create_tune(request, req: CreateTuneDTO):
    try:
        tune = Tune.objects.create(**req.dict())
    except Exception as err:
        return 400, {"message": "error", "err": "not tunes in db"}
    return 201, tune


@router.post("/update-user")
def update_user(request, req: UpdateUserDTO):    
    try:
        tg_user = TGUser.objects.get(tg_user_id=req.tg_user_id)
        if req.count_generations is not None:
            tg_user.count_generations = req.count_generations
        if req.is_learn_model is not None:
            tg_user.is_learn_model = req.is_learn_model 
        if req.referal is not None:
            tg_user.referal = req.referal
        if req.god_mod is not None:
            tg_user.god_mod = req.god_mod
        if req.effect is not None:
            tg_user.effect = req.effect
        if req.tune_id is not None:
            tg_user.tune_id = req.tune_id
        if req.god_mod_text is not None:
            tg_user.god_mod_text = req.god_mod_text
        if req.category is not None:
            tg_user.category = req.category
        if req.gender is not None:
            tg_user.gender = req.gender
        if req.count_video_generations is not None:
            tg_user.count_video_generations = req.count_video_generations
        tg_user.save()
        return {
            "tg_user_id": tg_user.tg_user_id, 
            "count_generations": tg_user.count_generations, 
            "is_learn_model": tg_user.is_learn_model,
            "god_mod": tg_user.god_mod,
            "referal": tg_user.referal,
            "effect": tg_user.effect,
            "tune_id": tg_user.tune_id,
            "god_mod_text": tg_user.god_mod_text,
            "category": tg_user.category,
            "gender": tg_user.gender,
            "count_video_generations": tg_user.count_video_generations,
        }
    except TGUser.DoesNotExist:
        return {"message": "error", "err": "User not found"}
    except Exception as err:
        return {"message": "error", "err": str(err)}


@router.post("/create-img-path", response={201: ImageDTO, 400: ErrorDTO})
def create_img_path(request, create_image: CreateImageDTO):
    try:
        user = TGUser.objects.get(tg_user_id=create_image.image.tg_user_id)
        images = Image.objects.filter(tg_user=user)
        if images.count() >= 10:
            images.delete()
        
        cln = Image.objects.create(
            tg_user=user,
            img_path=create_image.image.path,
        )
    except TGUser.DoesNotExist:
        return 400, {"message": "error", "err": "User not found"}
    except Exception as err:
        return 400, {"message": "error", "err": str(err)}
    
    return 201, ImageDTO(path=cln.img_path, tg_user_id=cln.tg_user.tg_user_id)


@router.get("/user-images/{tg_user_id}", response={200: list[ImageDTO], 400: ErrorDTO})
def get_user_images(request, tg_user_id: str):
    try:
        tg_user = TGUser.objects.get(tg_user_id=tg_user_id)
        images = Image.objects.filter(tg_user=tg_user)
        image_dto_list = [ImageDTO(path=image.img_path, tg_user_id=image.tg_user.tg_user_id) for image in images]
        return 200, image_dto_list
    
    except TGUser.DoesNotExist:
        return 400, {"message": "error", "err": str(err)}
    except Exception as err:
        return 400, {"message": "error", "err": str(err)}
    
    
@router.get("/categories/{gender}", response={200: list[CategoryDTO], 400: ErrorDTO})
def get_categories(request, gender: str):
    try:
        categories = Category.objects.filter(gender=gender).prefetch_related("promts")

        category_list = [
            {
                "name": category.name,
                "slug": category.slug,
                "gender": category.gender,
                "promts": [{"text": p.text} for p in category.promts.all()]
            }
            for category in categories
        ]

        return 200, category_list

    except Exception as err:
        return 400, {"message": "error", "err": str(err)}
    
    
@router.delete("/delete-user-images/{tg_user_id}", response={200: dict, 400: ErrorDTO, 404: ErrorDTO})
def delete_user_images(request, tg_user_id: str):
    try:
        user = TGUser.objects.get(tg_user_id=tg_user_id)
        
        deleted_count, _ = Image.objects.filter(tg_user=user).delete()
        
        if deleted_count == 0:
            return 404, {"message": "error", "err": "No images found for this user."}
        
        return 200, {"message": "error", "err": f"Deleted {deleted_count} images successfully."}

    except TGUser.DoesNotExist:
        return 404, {"message": "error", "err": "User not found"}
    except Exception as err:
        return 400, {"message": "Error deleting images", "err": str(err)}
