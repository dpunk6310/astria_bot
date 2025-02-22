import httpx
import asyncio

from core.logger.logger import get_logger


log = get_logger()

API_URL = "https://queue.fal.run/fal-ai/kling-video/v1.6/pro/image-to-video"
HEADERS = {
    "Authorization": "Key ed25032b-185e-4289-9495-d0b15dafc4dc:438277be849f5a74d83001d5537987cc",
    "Content-Type": "application/json"
}

async def generate_video_from_image(image_url: str) -> str:
    """Отправляет изображение в API и возвращает ссылку на видео."""
    data = {
        "prompt": "bring the photo to life",
        "image_url": image_url
    }
    try:
        async with httpx.AsyncClient() as client:
            # Шаг 1: Отправка изображения в API
            res = await client.post(url=API_URL, json=data, headers=HEADERS)
            if not res or res.status_code == 400:
                log.error(f"ошибка Отправка изображения в API {res.text}")
                return None
            out_data = res.json()
            status_url = out_data.get("status_url")
            response_url = out_data.get("response_url")
            
            if not status_url or not response_url:
                log.error("Не удалось получить URL-адреса из ответа API.")
                return None
            
            # Шаг 2: Ожидание завершения обработки
            i = 1
            while True:
                await asyncio.sleep(10)  # Используем asyncio.sleep вместо time.sleep
                r2 = await client.get(url=status_url, headers=HEADERS)
                if not r2 or r2.status_code == 400:
                    log.error(f"Ошибка Ожидание завершения обработки {res.text}")
                if not r2.is_success:
                    log.error("Ошибка при получении статуса обработки.")
                    return None
                
                r2_data = r2.json()
                status = r2_data.get("status")
                
                if status in ["IN_PROGRESS", "IN_QUEUE"]:
                    log.info(f"Попытка {i}... Видео еще создается.")
                    i += 1
                    continue
                elif status == "COMPLETED":
                    break
                else:
                    log.error(f"Неизвестный статус обработки: {status}")
                    return None
            
            # Шаг 3: Получение результата
            response = await client.get(response_url, headers=HEADERS)
            if not response or response.status_code == 400:
                log.error(f"Ошибка запроса на получени видео {response.text}")
                return None
            res_data = response.json()
            video_url = res_data.get("video", {}).get("url")
            if not video_url:
                log.error("Не удалось получить ссылку на видео.")
                return None
            
            return video_url
    except Exception as e:
        log.error(f"Непредвиденная ошибка: {e}", exc_info=True)
    
    return None