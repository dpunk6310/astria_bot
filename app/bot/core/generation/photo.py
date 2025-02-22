import asyncio
from uuid import uuid4
import os

import httpx
import requests

from core.logger.logger import get_logger


API_URL = 'https://api.astria.ai/tunes'
headers = {
    'Authorization': f'Bearer sd_L7JgJDHjtEJL1pgpXuPRoVjYNbJtGg',
}
log = get_logger()


async def learn_model_api(images: list[str], gender: str):
    data = {
        "tune[title]": str(uuid4()),
        "tune[name]": gender,
        "tune[base_tune_id]": 1504944,
        "tune[model_type]": "lora",
        "tune[preset]": "flux-lora-portrait",
        "tune[training_face_correct]": "true",
        "tune[steps]": 400,
        "tune[callback]": "https://webhook.site/f9674fa9-1bd3-4e31-b6b5-624dd7f045e9",
    }
    files = []
    for image in images:
        image_data = load_image(image)  
        files.append(("tune[images][]", image_data))
        os.remove(image)
                        
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(API_URL, data=data, files=files, headers=headers)
        except Exception as err:
            log.error(f"Ошибка обучения: {err}")
            return None
        return response.json()


def load_image(file_path):
    with open(file_path, "rb") as f:
        return f.read()
    
    
async def generate_images(tune_id: int, promt: str, effect: str = None):
    attempts = 0
    delay = 8
    max_attempts = 1000
    data = {
        'prompt[text]': f'<lora:{tune_id}:1> {promt}',
        # 'prompt[steps]': 40,
        'prompt[super_resolution]': "true",
        'prompt[inpaint_faces]': "true",
        'prompt[num_images]': 3,
        'prompt[w]': 896,
        'prompt[h]': 1152
    }
    if effect is not None:
        data['prompt[style]'] = effect
    while attempts < max_attempts:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"https://api.astria.ai/tunes/{tune_id}/prompts", data=data, headers=headers)
                if response and response.status_code not in [400, 502, 404]:
                    return response.json()
                attempts += 1
            except Exception as err:
                log.error(f"Ошибка получения ответа от отправки на генерации фото: {err} {response.text}")
                await asyncio.sleep(delay)
                attempts += 1
                continue
    return None
                    


def load_image(file_path):
    with open(file_path, "rb") as f:
        return f.read()
    
    
async def wait_for_generation(prompt_id):
    """Асинхронное ожидание завершения генерации изображения"""
    attempts = 0
    delay = 8
    max_attempts = 1000

    while attempts < max_attempts:
        try:
            async with httpx.AsyncClient() as client:
                status_response = await client.get(
                    f"https://api.astria.ai/prompts/{prompt_id}",
                    headers=headers
                )
                status_response.raise_for_status()
                status_data = status_response.json()
                if status_data.get('images') and len(status_data['images']) > 0:
                    return status_data['images']

                if status_data.get('status') == 'failed':
                    return None

                await asyncio.sleep(delay)
                attempts += 1

        except Exception as err:
            log.error(f"Ошибка получения ответа от ожидания генерации фото: {err} {status_response.text}")
            await asyncio.sleep(delay)
            attempts += 1


async def wait_for_training(tune_id: int):
    attempts = 0
    max_attempts = 2000
    delay = 30  

    while attempts < max_attempts:
        try:
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://api.astria.ai/tunes/{tune_id}", headers=headers)
                response.raise_for_status()
                status_data = response.json()

            if status_data.get("trained_at") is not None:
                return True

            await asyncio.sleep(delay)
            attempts += 1

        except Exception as err:
            log.error(f"Ошибка получения ответа от обучения модели: {err} {response.text}")
            await asyncio.sleep(delay)
            attempts += 1

    return False