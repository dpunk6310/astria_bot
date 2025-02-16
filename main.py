import requests
import time


url = "https://queue.fal.run/fal-ai/kling-video/v1.6/pro/image-to-video"
headers = {
    "Authorization": "Key ed25032b-185e-4289-9495-d0b15dafc4dc:438277be849f5a74d83001d5537987cc",
    "Content-Type": "application/json"
}

data = {
    "prompt": "A stylish woman walks down a Tokyo street filled with warm glowing neon and animated city signage. She wears a black leather jacket, a long red dress, and black boots, and carries a black purse.",
    "image_url": "https://api.telegram.org/file/bot8003935139:AAGFzQ-zB3_-mn2GhzaTsSd6G-3UVJ9u_GM/file_56.jpg"
}

res = requests.post(url=url, json=data, headers=headers)
print(res.text)
if res.status_code == 200:
    out_data = res.json()
    request_id = out_data.get("request_id")
    response_url = out_data.get("response_url")
    status_url = out_data.get("status_url")
    
    r2 = requests.get(url=status_url, headers=headers)
    
    i = 1
    while True:
        r2 = requests.get(url=status_url, headers=headers)
        if r2:
            r2_data = r2.json()
            if r2.status_code == 202 or r2_data.get("status") == "IN_PROGRESS":
                print(f"Попытка {i}")
                i += 1
                time.sleep(1)
                continue
            if r2.status_code == 200 or r2_data.get("status") == "COMPLETED":
                break
    response = requests.get(response_url, headers=headers)
    res_data = response.json()
    video_url = res_data.get("video").get("url")
    print(video_url)