import httpx


HEADERS = {
    "Authorization": "Bearer HU7g7_jkbvjv6342JBKb_edjfn3gkj_3242kjbgkdkjgb_6568uyV_iyg"
}

GENERATE_IMAGES_URL = "http://212.237.217.54:82/api/generate-images"


async def generate_images_v2(
    prompt: str, 
    chat_id: int, 
    effect: str,
    tune_id: int,
):
    payload = {
        "api_name": "astria",
        "tune_id": tune_id,
        "prompt": prompt,
        "effect": effect,
        "chat_id": chat_id
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=GENERATE_IMAGES_URL,
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