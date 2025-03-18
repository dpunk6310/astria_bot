from typing import Optional

from ninja import Schema


class CreatePaymentDTO(Schema):
    tg_user_id: str
    payment_id: str
    сount_generations: int
    count_video_generations: Optional[int]
    amount: str
    learn_model: bool
    is_first_payment: bool
    promo: bool
    count_generations_for_gift: int
    count_generations_video_for_gift: Optional[int]

    
class PaymentDTO(Schema):
    tg_user_id: str
    payment_id: str
    status: bool
    сount_generations: int
    amount: str
    promo: bool
    count_generations_for_gift: int
    count_generations_video_for_gift: Optional[int]
