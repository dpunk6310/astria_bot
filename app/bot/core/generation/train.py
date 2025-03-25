import httpx


HEADERS = {
    "Authorization": "Bearer HU7g7_jkbvjv6342JBKb_edjfn3gkj_3242kjbgkdkjgb_6568uyV_iyg"
}

TRAIN_MODEL_URL = "http://212.237.217.54:82/api/create-train"


async def create_train(
    chat_id: int, 
    images: list[str],
    gender: str,
    name: str,
):
    payload = {
        "api_name": "astria",
        "images": images,
        "gender": gender,
        "chat_id": chat_id,
        "name": name,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=TRAIN_MODEL_URL,
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