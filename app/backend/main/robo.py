
import json
import hashlib
from pathlib import Path

import requests


BASE_DIR = Path(__file__).resolve().parent.parent


def calculate_signature(*args) -> str:
    """Создание MD5 подписи."""
    return hashlib.md5(':'.join(str(arg) for arg in args).encode()).hexdigest()


def create_recurring_payment(
    merchant_login: str,
    merchant_password_1: str,
    invoice_id: int,
    previous_invoice_id: int,
    robokassa_recurring_url: str,
    amount: int = 990
):
    """Создание дочернего платежа."""
    file_path = BASE_DIR / "media" / "payload.json"
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    index = 0
    description = "Продление подписки"
    for i, v in enumerate(data):
        if v.get("name") == "Продление подписки":
            index = i
            break
    
    pay_data = json.dumps({
        "items": [
            data[index]
        ]
    })
    signature = calculate_signature(merchant_login, amount, invoice_id, pay_data, merchant_password_1)
    
    data = {
        "MerchantLogin": merchant_login,
        "InvoiceID": invoice_id,
        "PreviousInvoiceID": previous_invoice_id,
        "Description": description,
        "SignatureValue": signature,
        "OutSum": amount,
        "Receipt": pay_data
    }

    response = requests.post(url=robokassa_recurring_url, data=data)
    return response