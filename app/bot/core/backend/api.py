from ..client import client
from data.config import DJANGO_URL


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
    is_learn_model: bool = None
) -> dict:
    response = await client.post_request(url=DJANGO_URL+"/api/main/update-user", data={
        "tg_user_id": tg_user_id,
        "count_generations": count_generations,
        "is_learn_model": is_learn_model
    })
    return response


async def get_tunes(
    tg_user_id: str,
) -> dict:
    response = await client.get_request(url=DJANGO_URL+f"/api/main/get-tunes/{tg_user_id}")
    return response


async def get_price_list() -> dict:
    response = await client.get_request(url=DJANGO_URL+f"/api/main/get-prices-list")
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
    amount: str
) -> dict:
    response = await client.post_request(url=DJANGO_URL+"/api/main/create-payment", data={
        "tg_user_id": tg_user_id,
        "payment_id": payment_id,
        "сount_generations": сount_generations,
        "amount": amount,
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
    response = await client.get_request(
        url=DJANGO_URL+f"/api/main/get-user/{tg_user_id}"
    )
    return response


async def delete_user_images(
    tg_user_id: str,
) -> dict:
    response = await client.delete_request(
        url=DJANGO_URL+f"/api/main/delete-user-images/{tg_user_id}"
    )
    return response
