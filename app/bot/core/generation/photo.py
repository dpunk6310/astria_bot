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


async def learn_model_api(images: list[str], gender: str) -> dict:
    """ Обучает модель на основе переданных изображений и указанного пола.
    """
    model_title = str(uuid4())
    attempts = 0
    delay: int = 5
    max_attempts: int = 5

    # Подготовка данных для запроса
    data = {
        "tune[title]": model_title,
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
        try:
            image_data = load_image(image)  
            files.append(("tune[images][]", image_data))
            log.info(f"Изображение {image} успешно загружено для обучения модели.")
        except Exception as err:
            log.error(f"Ошибка загрузки изображения {image}: {err}")
            continue 
        finally:
            try:
                os.remove(image)
                log.info(f"Изображение {image} удалено после загрузки.")
            except Exception as err:
                log.error(f"Ошибка удаления изображения {image}: {err}")

    if not files:
        log.error("Нет доступных изображений для обучения модели.")
        return None

    log.info(f"Начало обучения модели с названием '{model_title}' для пола '{gender}'.")

    async with httpx.AsyncClient() as client:
        while attempts < max_attempts:
            attempts += 1
            try:
                log.info(f"Попытка {attempts}/{max_attempts}: отправка запроса на обучение модели...")
                response = await client.post(API_URL, data=data, files=files, headers=headers)
                response.raise_for_status() 
                return response.json()
            except httpx.HTTPStatusError as err:
                log.error(f"Ошибка HTTP при обучении модели: {err}")
            except httpx.RequestError as err:
                log.error(f"Ошибка соединения при обучении модели: {err}")
            except Exception as err:
                log.error(f"Неожиданная ошибка при обучении модели: {err}")

            if attempts < max_attempts:
                log.info(f"Повторная попытка через {delay} секунд...")
                await asyncio.sleep(delay)
            else:
                log.warning(f"Достигнуто максимальное количество попыток ({max_attempts}). Обучение модели прервано.")

    return None



def load_image(file_path):
    with open(file_path, "rb") as f:
        return f.read()
    
    
async def generate_images(tune_id: int, prompt: str, effect: str = None) -> dict:
    attempts = 0
    delay = 8
    max_attempts = 10
    data = {
        'prompt[text]': f'<lora:{tune_id}:1> {prompt}',
        'prompt[super_resolution]': "true",
        'prompt[inpaint_faces]': "true",
        'prompt[num_images]': 3,
        'prompt[w]': 896,
        'prompt[h]': 1152
    }
    if effect is not None:
        data['prompt[style]'] = effect

    log.info(f"Начало генерации изображений для tune_id={tune_id} с промтом: '{prompt}'")

    while attempts < max_attempts:
        async with httpx.AsyncClient() as client:
            try:
                log.info(f"Попытка {attempts + 1}/{max_attempts}: отправка запроса на генерацию изображений")
                response = await client.post(
                    f"https://api.astria.ai/tunes/{tune_id}/prompts",
                    data=data,
                    headers=headers
                )
                response.raise_for_status()
                log.info("Запрос успешно выполнен, получен ответ от сервера")
                return response.json()
            except httpx.HTTPStatusError as err:
                log.warning(f"Ошибка HTTP при запросе: {err} {data} {response.text}")
            except Exception as err:
                log.warning(f"Неожиданная ошибка при запросе: {err}")
            finally:
                attempts += 1
                if attempts < max_attempts:
                    log.info(f"Повторная попытка через {delay} секунд...")
                    await asyncio.sleep(delay)
                else:
                    log.warning("Достигнуто максимальное количество попыток. Генерация изображений прервана.")
    return None
                    


def load_image(file_path):
    with open(file_path, "rb") as f:
        return f.read()
    
    
async def wait_for_generation(prompt_id: int):
    """ Асинхронное ожидание завершения генерации изображения по указанному prompt_id.
    """
    attempts = 0
    delay: int = 8
    max_attempts: int = 1000

    log.info(f"Начало ожидания завершения генерации изображения для prompt_id={prompt_id}.")

    while attempts < max_attempts:
        attempts += 1
        try:
            log.info(f"Попытка {attempts}/{max_attempts}: проверка статуса генерации...")
            
            async with httpx.AsyncClient() as client:
                status_response = await client.get(
                    f"https://api.astria.ai/prompts/{prompt_id}",
                    headers=headers
                )
                status_response.raise_for_status() 
                status_data = status_response.json()

            if status_data.get('images') and len(status_data['images']) > 0:
                log.info(f"Генерация изображения для prompt_id={prompt_id} успешно завершена.")
                return status_data['images']

            if status_data.get('status') == 'failed':
                log.error(f"Генерация изображения для prompt_id={prompt_id} завершилась с ошибкой.")
                return None

            log.info(f"Генерация изображения для prompt_id={prompt_id} еще не завершена. Повторная проверка через {delay} секунд...")
            await asyncio.sleep(delay)

        except httpx.HTTPStatusError as err:
            log.error(f"Ошибка HTTP при проверке статуса генерации: {err} {status_response.text}")
        except httpx.RequestError as err:
            log.error(f"Ошибка соединения при проверке статуса генерации: {err}")
        except Exception as err:
            log.error(f"Неожиданная ошибка при проверке статуса генерации: {err}")

        if attempts < max_attempts:
            await asyncio.sleep(delay)
        else:
            log.warning(f"Достигнуто максимальное количество попыток ({max_attempts}). Генерация изображения не завершена.")

    return None


async def wait_for_training(tune_id: int) -> bool:
    """ Ожидает завершения обучения модели по указанному tune_id.
    """
    attempts = 0
    delay: int = 30
    max_attempts: int = 2000

    log.info(f"Начало ожидания завершения обучения модели с tune_id={tune_id}.")

    while attempts < max_attempts:
        attempts += 1
        try:
            log.info(f"Попытка {attempts}/{max_attempts}: проверка статуса обучения...")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://api.astria.ai/tunes/{tune_id}", headers=headers)
                response.raise_for_status() 
                status_data = response.json()

            if status_data.get("trained_at") is not None:
                log.info(f"Обучение модели с tune_id={tune_id} успешно завершено.")
                return True

            log.info(f"Обучение модели с tune_id={tune_id} еще не завершено. Повторная проверка через {delay} секунд...")
            await asyncio.sleep(delay)

        except httpx.HTTPStatusError as err:
            log.error(f"Ошибка HTTP при проверке статуса обучения: {err}")
        except httpx.RequestError as err:
            log.error(f"Ошибка соединения при проверке статуса обучения: {err}")
        except Exception as err:
            log.error(f"Неожиданная ошибка при проверке статуса обучения: {err}")

        if attempts < max_attempts:
            await asyncio.sleep(delay)
        else:
            log.warning(f"Достигнуто максимальное количество попыток ({max_attempts}). Обучение модели не завершено.")

    return False