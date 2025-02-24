import json
import base64
import hmac
import hashlib
from typing import List
from unicodedata import decimal

import requests
import os


def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


def create_jwt_token(header: dict, payload: dict, secret_key: str) -> str:
    header_encoded = base64url_encode(json.dumps(header, separators=(',', ':')).encode())
    payload_encoded = base64url_encode(json.dumps(payload, separators=(',', ':')).encode())
    signature_data = f"{header_encoded}.{payload_encoded}".encode()
    secret = secret_key.encode()

    algorithm = header.get("alg", "MD5").lower()

    hash_functions = {
        "md5": hashlib.md5,
        "ripemd160": hashlib.new("ripemd160"),
        "sha1": hashlib.sha1,
        "sha256": hashlib.sha256,
        "sha384": hashlib.sha384,
        "sha512": hashlib.sha512,
    }

    if algorithm not in hash_functions:
        raise ValueError("Unsupported algorithm")

    signature = hmac.new(secret, signature_data, hash_functions[algorithm]).digest()
    # print(signature_data)
    signature_encoded = base64url_encode(signature)
    # print(signature_encoded)

    return f'"{header_encoded}.{payload_encoded}.{signature_encoded}"'


def send_invoice_request(
    merchant_login: str,
    password1: str,
    payload: dict,
):
    header = {
        "typ": "JWT",
        "alg": "MD5"
    }

    secret_key = f"{merchant_login}:{password1}"
    jwt_token = create_jwt_token(header, payload, secret_key)

    url = "https://services.robokassa.ru/InvoiceServiceWebApi/api/CreateInvoice"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=jwt_token, headers=headers)
    return response.json()


def generate_payment_link(
    merchant_login: str,  # Merchant login
    merchant_password_1: str,  # Merchant password
    cost: decimal,  # Cost of goods, RU
    number: int,  # Invoice number
    description: str,  # Description of the purchase
    items: List[dict],
    payload=None,
) -> str:
    if payload is None:
        payload = {
            "MerchantLogin": merchant_login,
            "InvoiceType": "OneTime",
            "Culture": "ru",
            "InvId": number,
            "OutSum": cost,
            "Description": description,
            "InvoiceItems": items
        }
    response = send_invoice_request(
        merchant_login,
        merchant_password_1,
        payload,
    )
    if response["isSuccess"]:
        return response["url"]
    print(response)
    return None


# if __name__ == "__main__":

#     import environ
#     from pathlib import Path

#     BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent

#     env = environ.Env()
#     env.read_env(str(BASE_DIR / ".env"))
#     ROBOKASSA_MERCHANT_ID = env.str("ROBOKASSA_MERCHANT_ID", "")
#     ROBOKASSA_PASSWORD1 = env.str("ROBOKASSA_PASSWORD1", "")
#     ROBOKASSA_PASSWORD2 = env.str("ROBOKASSA_PASSWORD2", "")
#     ROBOKASSA_TEST_PASSWORD1 = env.str("ROBOKASSA_TEST_PASSWORD1", "")
#     ROBOKASSA_TEST_PASSWORD2 = env.str("ROBOKASSA_TEST_PASSWORD2", "")
#     current_dir = os.path.dirname(os.path.realpath(__file__))
#     file_path = os.path.join(current_dir, 'payload.json')
#     with open(file_path, 'r', encoding='utf-8') as file:
#         data = json.load(file)
#     payment_link = generate_payment_link(
#         ROBOKASSA_MERCHANT_ID,
#         ROBOKASSA_PASSWORD1,
#         490, # Деньга столько же
#         10, # рандомное число 1 до 2 147 483 647
#         "Описание тестовое",
#         items=[data[1]] # индекс из файла
#     )
#     print(payment_link)
