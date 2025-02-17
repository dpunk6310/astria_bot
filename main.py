import requests

url = "https://queue.fal.run/fal-ai/kling-video/requests/922735d3-8896-4ca7-ae4d-db256cb4b216"

HEADERS = {
    "Authorization": "Key ed25032b-185e-4289-9495-d0b15dafc4dc:438277be849f5a74d83001d5537987cc",
    "Content-Type": "application/json"
}

r = requests.get(url=url, headers=HEADERS)
print(r.text)