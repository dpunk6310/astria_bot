import httpx


HEADERS = {
    "Authorization": "Bearer HU7g7_jkbvjv6342JBKb_edjfn3gkj_3242kjbgkdkjgb_6568uyV_iyg"
}

GENERATE_PFP_URL = "http://212.237.217.54:82/api/generate-pfp"


async def generate_pfp_v2(
    image_url: str, 
    chat_id: int, 
    effect: str,
    tune_id: int,
    gender: str,
    w: str = "",
    h: str = "",
):
    payload = {
        "api_name": "astria",
        "tune_id": tune_id,
        "gender": gender,
        "effect": effect,
        "chat_id": chat_id,
        "image_url": image_url,
        "w": w,
        "h": h,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=GENERATE_PFP_URL,
            headers=HEADERS,
            json=payload,
            timeout=30,
        )
        print(response.text)

        try:
            response.raise_for_status()
        except Exception as err:
            print(err)
            return None
        return response
    return None