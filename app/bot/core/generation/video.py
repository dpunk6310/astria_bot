import requests
import time


API_URL = "https://queue.fal.run/fal-ai/kling-video/v1.6/pro/image-to-video"
HEADERS = {
    "Authorization": "Key ed25032b-185e-4289-9495-d0b15dafc4dc:438277be849f5a74d83001d5537987cc",
    "Content-Type": "application/json"
}


def generate_video_from_image(image_url: str) -> str:
    """ Отправляет изображение в API и возвращает ссылку на видео.
    """
    data = {
        "prompt": "A stylish woman walks down a Tokyo street filled with warm glowing neon and animated city signage. "
                  "She wears a black leather jacket, a long red dress, and black boots, and carries a black purse.",
        "image_url": image_url
    }
    try:
        res = requests.post(url=API_URL, json=data, headers=HEADERS)
        res.raise_for_status()
        
        out_data = res.json()
        status_url = out_data.get("status_url")
        response_url = out_data.get("response_url")
        
        if not status_url or not response_url:
            raise ValueError("Не удалось получить URL-адреса из ответа API.")
        
        i = 1
        while True:
            time.sleep(1)
            r2 = requests.get(url=status_url, headers=HEADERS)
            if not r2.ok:
                raise ValueError("Ошибка при получении статуса обработки.")
            
            r2_data = r2.json()
            status = r2_data.get("status")
            
            if status == "IN_PROGRESS":
                print(f"Попытка {i}... Видео еще создается.")
                i += 1
                continue
            elif status == "COMPLETED":
                break
            else:
                raise ValueError(f"Неизвестный статус обработки: {status}")
        
        response = requests.get(response_url, headers=HEADERS)
        response.raise_for_status()
        res_data = response.json()
        video_url = res_data.get("video", {}).get("url")
        
        if not video_url:
            raise ValueError("Не удалось получить ссылку на видео.")
        
        return video_url
    
    except requests.RequestException as e:
        print(f"Ошибка запроса: {e}")
    except ValueError as e:
        print(f"Ошибка обработки данных: {e}")
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
    
    return ""