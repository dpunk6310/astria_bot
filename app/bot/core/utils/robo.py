import json
import base64
import hmac
import hashlib
from typing import List
from unicodedata import decimal
from urllib.parse import urlencode

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


def calculate_signature(*args) -> str:
    """Создание MD5 подписи."""
    return hashlib.md5(':'.join(str(arg) for arg in args).encode()).hexdigest()


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


def generate_subscribe_payment_link(
    merchant_login: str,  
    merchant_password_1: str, 
    cost: decimal,  
    number: int, 
    description: str,
    items: dict
) -> str:
    """Генерация ссылки для переадресации пользователя на оплату."""
    robokassa_payment_url: str = 'https://auth.robokassa.ru/Merchant/Index.aspx'
    r = json.dumps(items)
    signature = calculate_signature(merchant_login, cost, number, r, merchant_password_1)

    data = {
        'MerchantLogin': merchant_login,
        'OutSum': cost,
        'invoiceID': number,
        'Description': description,
        'SignatureValue': signature,
        'Recurring': 'true',
        'Receipt': r
    }
    return f'{robokassa_payment_url}?{urlencode(data)}'

