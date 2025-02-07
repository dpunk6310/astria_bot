from ninja import Router
from django.db.utils import IntegrityError
from loguru import logger as log

from telegram_api.api import send_message_successfully_pay
from config.settings import BOT_TOKEN
from dto.user import CreateUserDTO, UserDTO, UpdateUserDTO
from dto.image import CreateImageDTO, ImageDTO
from dto.payment import PaymentDTO, CreatePaymentDTO
from dto.err import ErrorDTO, SuccessDTO
from .models import TGUser, Image, Payment
# from config.loader import telegram_api


router = Router()


@router.get("/healthcheck")
def healthcheck(request):
    return {"msg": "Ok Ok"}


@router.post("/create", response={201: UserDTO, 400: ErrorDTO})
def create_user(request, create_user: CreateUserDTO):
    try:
        cln = TGUser.objects.create(**create_user.dict().get("user"))
    except IntegrityError as err:
        return 400, {"message": "error", "err": "such a tg user already exists"}
    return 201, cln


@router.post("/create-payment", response={201: PaymentDTO, 400: ErrorDTO})
def create_payment(request, cr_pay: CreatePaymentDTO):
    try:
        payment = Payment.objects.create(**cr_pay.dict())
        return 201, payment
    except Exception as err:
        log.error(err)
        return 400, {"message": "error", "err": str(err)}
    
    
@router.post("/get-payment/{payment_id}", response={200: PaymentDTO, 400: ErrorDTO})
def get_payment(request, payment_id: str):
    try:
        payment = Payment.objects.get(payment_id=payment_id)
        return 200, payment
    except Exception as err:
        log.error(err)
        return 400, {"message": "error", "err": str(err)}


@router.post("/payment", response={200: SuccessDTO, 400: ErrorDTO})
def payment_received(request):
    try:
        raw_body = request.body.decode("utf-8", errors="ignore")  # Декодируем в строку
        content_type = request.headers.get("Content-Type", "Unknown")  # Проверяем заголовок
        log.debug(f"Content-Type: {content_type}")
        log.debug(f"Raw body: {raw_body}")
        data = request.POST.dict()
        payment = Payment.objects.get(payment_id=data["inv_id"])
        payment.status = True
        payment.save()
        # result = send_message_successfully_pay(BOT_TOKEN, payment.tg_user_id)
        log.debug("ОПЛАТА УСПЕШНА!")
        tg_user: TGUser = TGUser.objects.get(
            tg_user_id=payment.tg_user_id,
        )
        tg_user.count_generations += payment.сount_generations
        tg_user.save()

        return 200, {"status": "ok", "message": "Success"}
    except Payment.DoesNotExist:
        return 400, {"message": "error", "err": "payment not found"}
    except TGUser.DoesNotExist:
        return 400, {"message": "error", "err": "user not found"}


@router.get("/get-user", response={200: UserDTO, 400: ErrorDTO})
def get_user(request, tg_user_id: str):
    try:
        cln = TGUser.objects.get(tg_user_id=tg_user_id)
    except IntegrityError as err:
        return 400, {"message": "error", "err": "not user in db"}
    return 200, cln


@router.post("/update-count-gen")
def update_user(request, req: UpdateUserDTO):
    try:
        tg_user = TGUser.objects.get(tg_user_id=req.tg_user_id)
        tg_user.count_generations = req.count_generations 
        tg_user.save()
        return {"message": "success", "user": tg_user.tg_user_id, "count_generations": tg_user.count_generations}
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
            images.delete
        
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
