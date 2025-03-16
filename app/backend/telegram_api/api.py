import httpx


def send_message_successfully_pay(bot_token: str, chat_id: str, callback_data: str, button_text: str):
    payload = {
        "chat_id": chat_id,
        "text": "Поздравляю! Оплата завершена успешно ❤️\n\n"
                "Теперь доверься и последуй одному важному совету: "
                "внимательно прочитай инструкцию и действуй согласно ей, "
                "ведь именно это будет влиять на твой результат",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": button_text, "callback_data": callback_data}]
            ]
        },
        "parse_mode": "HTML"
    }
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        response = httpx.post(url=url, json=payload)
        return response.json()
    except Exception as e:
        return {"err": str(e)}


def send_promo_message(bot_token: str, chat_id: str, promocode_gen: str):
    payload = {
        "chat_id": chat_id,
        "text": """Ваш промокод: <code>{promocode_gen}</code>""".format(promocode_gen=promocode_gen),
        "parse_mode": "HTML"
    }
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        response = httpx.post(url=url, json=payload)
        return response.json()
    except Exception as e:
        return {"err": str(e)}
