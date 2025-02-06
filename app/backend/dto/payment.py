from ninja import Schema


class CreatePaymentDTO(Schema):
    tg_user_id: str
    payment_id: str
    status: bool
    

class PaymentDTO(Schema):
    tg_user_id: str
    payment_id: str
    status: bool
