from ..client import client
from data.config import DJANGO_URL


async def create_user_db(
    tg_user_id: str,
    first_name: str,
    last_name: str,
    username: str,
) -> dict:
    response = await client.post_request(url=DJANGO_URL+"/api/main/create", data={
        "user": {
            "tg_user_id": str(tg_user_id),
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
        }
    })
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


async def get_user_images(
    tg_user_id: str,
) -> dict:
    response = await client.get_request(
        url=DJANGO_URL+f"/api/main/user-images/{tg_user_id}"
    )
    return response


async def delete_user_images(
    tg_user_id: str,
) -> dict:
    response = await client.delete_request(
        url=DJANGO_URL+f"/api/main/delete-user-images/{tg_user_id}"
    )
    return response
