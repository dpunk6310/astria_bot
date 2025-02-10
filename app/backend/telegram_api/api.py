# # third-party imports
# import requests
# import json

# # standart imports
# from typing import Union


# class TelegramSyncClient:
#     """Client for requests to Telegram API"""

#     _base_url = "https://api.telegram.org/bot{token}/{method_name}"

#     def __init__(self, token):
#         self._token = token

#     def _get_url(self, method_name: str):
#         """Get method url."""
#         return self._base_url.format(
#             token=self._token,
#             method_name=method_name,
#         )

#     def _request(
#         self,
#         url: str,
#         params: dict = {},
#     ) -> dict:
#         """Send request to API."""

#         return requests.get(
#             url,
#             params=params,
#         ).json()

#     def send_message(
#         self,
#         chat_id: Union[int, str],
#         text: str,
#         reply_markup: dict = {},
#     ):
#         """Send message."""

#         return self._request(
#             self._get_url("sendMessage"),
#             params={
#                 "chat_id": chat_id,
#                 "text": text,
#                 "reply_markup": reply_markup,
#             }
#         )["result"]

#     def send_message_inline(
#         self,
#         chat_id: Union[int, str],
#         text: str,
#         button_text: str,
#         callback_data: str
#     ):
#         """Send message."""
#         reply_markup = {
#             "inline_keyboard": [[
#                 {"text": button_text, "callback_data": callback_data}
#             ]]
#         }

#         return self._request(
#             self._get_url("sendMessage"),
#             params={
#                 "chat_id": chat_id,
#                 "text": text,
#                 "reply_markup": json.dumps(reply_markup),
#             }
#         )

#     def pin_chat_message(
#         self,
#         chat_id: Union[int, str],
#         message_id: Union[int, str],
#         disable_notification: bool = False,
#     ):
#         """Pin chat message."""

#         return self._request(
#             self._get_url("pinChatMessage"),
#             params={
#                 "chat_id": chat_id,
#                 "message_id": message_id,
#                 "disable_notification": disable_notification,
#             },
#         )

#     def unpin_chat_message(
#         self,
#         chat_id: Union[int, str],
#         message_id: Union[int, str],
#     ):
#         """Unpin chat message."""

#         return self._request(
#             self._get_url("unpinChatMessage"),
#             params={
#                 "chat_id": chat_id,
#                 "message_id": message_id,
#             },
#         )


import httpx

def send_message_successfully_pay(bot_token: str, chat_id: str):
    payload = {
        "chat_id": chat_id,
        "text": "Поздравляю! Оплата завершена успешно ❤️\n\n"
                "Теперь доверься и последуй одному важному совету: "
                "внимательно прочитай инструкцию и действуй согласно ей, "
                "ведь именно это будет влиять на твой результат",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "Инструкция", "callback_data": "start_upload_photo"}]
            ]
        },
        "parse_mode": "Markdown"
    }
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        response = httpx.post(url=url, json=payload)
        return response.json()
    except Exception as e:
        return {"err": str(e)}
