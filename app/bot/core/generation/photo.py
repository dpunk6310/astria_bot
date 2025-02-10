import asyncio
from uuid import uuid4
import os

import httpx
from loguru import logger as log
import requests


API_URL = 'https://api.astria.ai/tunes'
headers = {
    'Authorization': f'Bearer sd_L7JgJDHjtEJL1pgpXuPRoVjYNbJtGg',
}


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
            log.error(err)
            return None
        return response.json()


def load_image(file_path):
    with open(file_path, "rb") as f:
        return f.read()
    
    
async def generate_images(tune_id: int, promt: str, effect: str = None):
    data = {
        'prompt[text]': f'<lora:{tune_id}:1> {promt}',
        # 'prompt[steps]': 40,
        'prompt[super_resolution]': "true",
        'prompt[inpaint_faces]': "true",
        'prompt[num_images]': 3
    }
    if effect is not None:
        data['prompt[style]'] = effect
    log.debug(data)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"https://api.astria.ai/tunes/{tune_id}/prompts", data=data, headers=headers)
        except Exception as err:
            log.error(err)
            return None
        return response.json()


def load_image(file_path):
    with open(file_path, "rb") as f:
        return f.read()
    
    
async def wait_for_generation(prompt_id):
    """Асинхронное ожидание завершения генерации изображения"""
    log.debug("\nОжидаем завершения генерации...")
    attempts = 0
    max_attempts = 400
    delay = 8  # интервал проверки в секундах

    while attempts < max_attempts:
        try:
            status_response = requests.get(
                f"https://api.astria.ai/prompts/{prompt_id}",
                headers=headers
            )
            status_response.raise_for_status()
            status_data = status_response.json()

            log.debug("Ответ от API:", status_data)

            if status_data.get('images') and len(status_data['images']) > 0:
                log.debug("✅ Генерация завершена!")
                return status_data['images']

            if status_data.get('status') == 'failed':
                log.debug("❌ Ошибка генерации:", status_data.get('error', 'Неизвестная ошибка'))
                return None

            log.debug(f"⏳ Прогресс: {attempts * delay} секунд")
            await asyncio.sleep(delay)
            attempts += 1

        except Exception as e:
            log.debug(f"❌ Ошибка проверки статуса: {str(e)}")
            await asyncio.sleep(delay)
            attempts += 1

    log.debug("❌ Превышено время ожидания генерации")
    return None


async def wait_for_training(tune_id: int):
    attempts = 0
    max_attempts = 1000
    delay = 30  

    while attempts < max_attempts:
        try: # 
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://api.astria.ai/tunes/{tune_id}", headers=headers)
                response.raise_for_status()
                status_data = response.json()

            if status_data.get("trained_at") is not None:
                log.debug("✅ Обучение завершено!")
                return True

            log.debug(f"⏳ Обучение в процессе... (попытка {attempts + 1})")
            await asyncio.sleep(delay)  # Асинхронная пауза вместо time.sleep()
            attempts += 1

        except Exception as e:
            log.debug(f"❌ Ошибка проверки статуса: {str(e)}")
            await asyncio.sleep(delay)
            attempts += 1

    log.debug("❌ Превышено время ожидания обучения")
    return False