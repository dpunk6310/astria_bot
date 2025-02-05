from uuid import uuid4
import httpx

headers = {'Authorization': f'Bearer sd_L7JgJDHjtEJL1pgpXuPRoVjYNbJtGg'}

def load_image(file_path):
    with open(file_path, "rb") as f:
        return f.read()

# Assuming `prompts` and `tune.images` are already defined in your context

data = {
    "tune[title]": str(uuid4()),
    "tune[name]": "man",
    "tune[base_tune_id]": 1504944,
    "tune[model_type]": "lora",
    # "token": "sks",
    "tune[preset]": "flux-lora-portrait",
    "tune[training_face_correct]": "true",
    "tune[steps]": 400,
    "tune[callback]": "https://webhook.site/f9674fa9-1bd3-4e31-b6b5-624dd7f045e9",
}

files = []

for image in ["./media/photos/2d7d77ca-f47f-4158-9962-a9bac25e6628_file_4.jpg", "./media/photos/7fb451e7-ed38-4ef1-9612-7fdefd7eafc3_file_5.jpg"]:
    image_data = load_image(image)  # Assuming image is a file path
    files.append(("tune[images][]", image_data))
    
API_URL = 'https://api.astria.ai/tunes'

async def send_request():
    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, data=data, files=files, headers=headers)
        response.raise_for_status()

        print(response.json())

# To run the asynchronous request
import asyncio
asyncio.run(send_request())
