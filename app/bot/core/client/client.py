import httpx

from loguru import logger as log


async def get_request(url: str) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 400:
                return None
            return response.json()
    except Exception as e:
        log.error(e)
        return None
    
    
async def delete_request(url: str) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(url)
            return response.json()
    except Exception as e:
        return {"err": str(e)}


async def post_request(url: str, data: dict, headers: dict = {}, files: dict = None) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            if headers == {}:
                headers = {'Content-Type': 'application/json'}
            response = await client.post(url, json=data, headers=headers, files=files)
            return response.json() 
    except Exception as e:
        log.error(e)
        return None
