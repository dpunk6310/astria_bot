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
    
    async with httpx.AsyncClient() as client:
        try:
            # Шаг 1: Отправка изображения в API
            log.info(f"Отправка изображения в API. image_url={image_url}")
            res = await client.post(url=API_URL, json=data, headers=HEADERS)
            res.raise_for_status()  # Вызовет исключение для статусов 4XX/5XX
            out_data = res.json()
            
            if not (status_url := out_data.get("status_url")) or not (response_url := out_data.get("response_url")):
                log.error(f"Не удалось получить URL-адреса из ответа API. response={res.text}")
                return None
            
            # Шаг 2: Ожидание завершения обработки
            log.info(f"Ожидание завершения обработки. status_url={status_url}")
            for i in range(1, 11):  # Ограничим количество попыток до 10
                await asyncio.sleep(10)
                r2 = await client.get(url=status_url, headers=HEADERS)
                r2.raise_for_status()
                
                r2_data = r2.json()
                status = r2_data.get("status")
                
                if status == "COMPLETED":
                    log.info("Обработка видео завершена.")
                    break
                elif status in ["IN_PROGRESS", "IN_QUEUE"]:
                    log.info(f"Попытка {i}... Видео еще создается. status={status}")
                    continue
                else:
                    log.error(f"Неизвестный статус обработки: {status}. r2_data={r2_data}")
                    return None
            else:
                log.error(f"Превышено количество попыток получения статуса. r2_data={r2_data}")
                return None
            
            # Шаг 3: Получение результата
            log.info(f"Получение результата. response_url={response_url}")
            response = await client.get(response_url, headers=HEADERS)
            response.raise_for_status()
            res_data = response.json()
            
            if not (video_url := res_data.get("video", {}).get("url")):
                log.error(f"Не удалось получить ссылку на видео. response={response.text}")
                return None
            
            log.info(f"Видео успешно создано. video_url={video_url}")
            return video_url
        
        except httpx.HTTPStatusError as e:
            log.error(f"Ошибка HTTP запроса: {e}. URL={e.request.url}, Статус={e.response.status_code}, Ответ={e.response.text}")
        except httpx.RequestError as e:
            log.error(f"Ошибка при выполнении запроса: {e}. URL={e.request.url if e.request else 'неизвестно'}")
        except KeyError as e:
            log.error(f"Отсутствует ожидаемый ключ в ответе API: {e}. Ответ={res.text if 'res' in locals() else 'неизвестно'}")
        except Exception as e:
            log.error(f"Непредвиденная ошибка: {e}. Тип ошибки: {type(e).__name__}")
    
    return None