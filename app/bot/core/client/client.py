import httpx


async def get_request(url: str) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status() 
            return response.json()
    except Exception as e:
        return {"err": str(e)}


async def post_request(url: str, data: dict, headers: dict = {}, files: dict = None) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            if headers == {}:
                headers = {'Content-Type': 'application/json'}
            response = await client.post(url, json=data, headers=headers, files=files)
            response.raise_for_status() 
            return response.json() 
    except Exception as e:
        return {"err": str(e)}
