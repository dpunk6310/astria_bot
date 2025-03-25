import httpx


HEADERS = {
    "Authorization": "Bearer HU7g7_jkbvjv6342JBKb_edjfn3gkj_3242kjbgkdkjgb_6568uyV_iyg"
}

GENERATE_VIDEO_URL = "http://212.237.217.54:82/api/generate-video"


async def generate_video(
    chat_id: int, 
    image_url: str,
):
    payload = {
        "api_name": "falai",
        "chat_id": chat_id,
        "image_url": image_url,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=GENERATE_VIDEO_URL,
            headers=HEADERS,
            json=payload,
        )
        try:
            response.raise_for_status()
        except Exception as err:
            print(err)
            return None
        return response
    return None