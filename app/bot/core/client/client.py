import httpx

from core.logger.logger import get_logger


log = get_logger()


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
        return None


async def post_request(url: str, data: dict, headers: dict = {}, files: dict = None) -> dict:
    for i in range(10):
        try:
            async with httpx.AsyncClient() as client:
                if headers == {}:
                    headers = {'Content-Type': 'application/json'}
                response = await client.post(url, json=data, headers=headers, files=files)
                if response and response.status_code == 201:
                    return response.json()
                log.error(response.text)
                continue
        except Exception as e:
            log.error(e)
            continue
