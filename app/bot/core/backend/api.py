from ..client import client
from data.config import DJANGO_URL

from loguru import logger as log


async def create_user_db(
    tg_user_id: str,
    first_name: str,
    last_name: str,
    username: str,
) -> dict:
    response = await client.post_request(url=DJANGO_URL+"/api/main/create", data={
        "tg_user_id": str(tg_user_id),
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
    })
    return response


async def create_tune(
    tg_user_id: str,
    tune_id: str,
    gender: str
) -> dict:
    response = await client.post_request(url=DJANGO_URL+"/api/main/create-tune", data={
        "tg_user_id": tg_user_id,
        "tune_id": tune_id,
        "gender": gender
    })
    return response


async def update_user(
    tg_user_id: str,
    count_generations: int = None,
    is_learn_model: bool = None,
    god_mod: bool = None,
    referal: str = None,
    effect: str = None,
    tune_id: str = None,
    god_mod_text: str = None,
    category: str = None,
    gender: str = None,
    count_video_generations: str = None
) -> dict:
    response = await client.post_request(url=DJANGO_URL+"/api/main/update-user", data={
        "tg_user_id": tg_user_id,
        "count_generations": count_generations,
        "is_learn_model": is_learn_model,
        "god_mod": god_mod,
        "referal": referal,
        "effect": effect,
        "tune_id": tune_id,
        "god_mod_text": god_mod_text,
        "category": category,
        "gender": gender,
        "count_video_generations": count_video_generations
    })
    return response


async def get_tunes(
    tg_user_id: str,
) -> dict:
    response = await client.get_request(url=DJANGO_URL+f"/api/main/get-tunes/{tg_user_id}")
    return response


async def get_price_list(type_price_list: str) -> dict:
    response = await client.get_request(url=DJANGO_URL+f"/api/main/get-prices-list/{type_price_list}")
    return response


async def get_avatar_price_list() -> dict:
    response = await client.get_request(url=DJANGO_URL+f"/api/main/get-avatar-price-list")
    return response

async def get_tune(
    tune_id: str,
) -> dict:
    response = await client.get_request(url=DJANGO_URL+f"/api/main/get-tune/{tune_id}")
    return response


async def create_img_path(
    tg_user_id: str,
    path: str,
) -> dict:
    response = await client.post_request(url=DJANGO_URL+"/api/main/create-img-path", data={
        "image": {
            "tg_user_id": str(tg_user_id),
            "path": path,
        }
    })
    return response


async def create_payment(
    tg_user_id: str,
    payment_id: str,
    сount_generations: int,
    amount: str,
    learn_model: bool = False,
    is_first_payment: bool = False,
) -> dict:
    response = await client.post_request(url=DJANGO_URL+"/api/main/create-payment", data={
        "tg_user_id": tg_user_id,
        "payment_id": payment_id,
        "сount_generations": сount_generations,
        "amount": amount,
        "learn_model": learn_model,
        "is_first_payment": is_first_payment,
    })
    return response


async def get_payment(
    payment_id: str,
) -> dict:
    response = await client.get_request(url=DJANGO_URL+f"/api/main/get-payment/{payment_id}")
    return response


async def get_user_images(
    tg_user_id: str,
) -> dict:
    response = await client.get_request(
        url=DJANGO_URL+f"/api/main/user-images/{tg_user_id}"
    )
    return response


async def get_user(
    tg_user_id: str,
) -> dict:
    try:
        response = await client.get_request(
            url=DJANGO_URL+f"/api/main/get-user/{tg_user_id}"
        )
        if not response:
            return None
    except Exception as err:
        return None
    return response


async def delete_user_images(
    tg_user_id: str,
) -> dict:
    response = await client.delete_request(
        url=DJANGO_URL+f"/api/main/delete-user-images/{tg_user_id}"
    )
    return response
