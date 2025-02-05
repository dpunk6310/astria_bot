from ..client import client
from ...data.config import DJANGO_URL


async def create_user_db(
    tg_user_id: str,
    first_name: str,
    last_name: str,
    username: str,
) -> dict:
    response = await client.post_request(url=DJANGO_URL, data={
        "tg_user_id": tg_user_id,
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
    })
    return response
