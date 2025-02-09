from ninja import Schema


class CreatePaymentDTO(Schema):
    tg_user_id: str
    payment_id: str
    сount_generations: int
    amount: str
    learn_model: bool
    

class PaymentDTO(Schema):
    tg_user_id: str
    payment_id: str
    status: bool
    сount_generations: int
    amount: str
