from openai import OpenAI

import httpx
from core.logger.logger import get_logger


log = get_logger()


def translate_promt(promt: str) -> str:
    client = OpenAI(api_key="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")

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system", 
                "content": "You are an assistant in creating good scripts for flux (for generating photos) and translating them into English. I'll write you a promt, it may be short - then you need to adapt it for the Flux neural network - add details, colors, and make the query more interesting. At the same time, I can send you a high-quality and detailed promt, then it doesn't need to be changed. The volume will speak about the quality. if the promt is large, it means that it does not need to be changed. in response, you need to send an improved promt in English, without unnecessary words, phrases, symbols, etc. if the promt from me is initially good, duplicate my promt in response."
            },
            {
                "role": "user",
                "content": promt
            }
        ]
    )
    return completion.choices[0].message.content


def translate_promt2(promt: str):
    data = { 
    "model":"gpt-4o", 
    "lang": "en", 
    "promt": "you need to describe the photo in promt for Flux describe everything except the person's features: clothes, surroundings, other things. The description should be 1 in 1, keeping all the clothes and other details. it is very important to do this efficiently, otherwise I will be fired from my job. in response, we received only a ready-made promt in English. Always answer without unnecessary symbols, like *, etc.",
    "messages":  
        [ 
          { 
            "role":"user", 
            "content":[ 
              { 
                "type": "text", 
                "text": promt
              } 
            ] 
          } 
        ] 
    }

    response = httpx.post("https://geminab.site/api/chatg", json=data, timeout=30)
    try:
        return response.json().get("choices")[0].get("message").get("content")
    except Exception as err:
        log.error(err)
        return promt
    
    
def get_image_prompt(image_url: str):
    data = {
        "model": "gpt-4o",
        "lang": "en",
        "prompt": "You are an assistant in creating good scripts for flux (for generating photos) and translating them into English. I'll write you a promt, it may be short - then you need to adapt it for the Flux neural network - add details, colors, and make the query more interesting. At the same time, I can send you a high-quality and detailed promt, then it doesn't need to be changed. The volume will speak about the quality. if the promt is large, it means that it does not need to be changed. in response, you need to send an improved promt in English, without unnecessary words, phrases, symbols, etc. if the promt from me is initially good, duplicate my promt in response.",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Describe the picture"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                    "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ]
    }

    response = httpx.post("https://geminab.site/api/chatg", json=data, timeout=30)

    try:
        return response.json().get("choices")[0].get("message").get("content")
    except Exception as err:
        log.error(err)
        return ""
