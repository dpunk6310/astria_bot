import httpx
import asyncio
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            res.raise_for_status()
            
            out_data = res.json()
            status_url = out_data.get("status_url")
            response_url = out_data.get("response_url")
            
            if not status_url or not response_url:
                logger.error("Не удалось получить URL-адреса из ответа API.")
                return None
            
            # Шаг 2: Ожидание завершения обработки
            i = 1
            while True:
                await asyncio.sleep(10)  # Используем asyncio.sleep вместо time.sleep
                r2 = await client.get(url=status_url, headers=HEADERS)
                if not r2.is_success:
                    logger.error("Ошибка при получении статуса обработки.")
                    return None
                
                r2_data = r2.json()
                status = r2_data.get("status")
                
                if status in ["IN_PROGRESS", "IN_QUEUE"]:
                    logger.info(f"Попытка {i}... Видео еще создается.")
                    i += 1
                    continue
                elif status == "COMPLETED":
                    break
                else:
                    logger.error(f"Неизвестный статус обработки: {status}")
                    return None
            
            # Шаг 3: Получение результата
            response = await client.get(response_url, headers=HEADERS)
            response.raise_for_status()
            res_data = response.json()
            print(res_data)
            video_url = res_data.get("video", {}).get("url")
            if not video_url:
                logger.error("Не удалось получить ссылку на видео.")
                return None
            
            return video_url
    
    except httpx.RequestError as e:
        logger.error(f"Ошибка запроса: {e}")
    except ValueError as e:
        logger.error(f"Ошибка обработки данных: {e}")
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}", exc_info=True)
    
    return None