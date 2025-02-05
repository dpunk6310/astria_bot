import requests


API_URL = 'https://api.astria.ai/tunes/2103900/prompts'

headers = {'Authorization': f'Bearer sd_L7JgJDHjtEJL1pgpXuPRoVjYNbJtGg'}

data = {
    'prompt[text]': '<lora:2103900:1> a painting of sks man / woman in the style of Van Gogh',
    'prompt[callback]': 'https://webhook.site/f9674fa9-1bd3-4e31-b6b5-624dd7f045e9'
}

response = requests.post(API_URL, headers=headers, data=data)
print(response)
print(response.text)