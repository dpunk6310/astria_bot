from typing import Optional
from datetime import datetime, date

from django.utils.timezone import now

from ninja import Schema


class UserDTO(Schema):
    tg_user_id: str
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    count_generations: Optional[int]
    is_learn_model: Optional[bool]
    god_mod: bool
    photo_from_photo: bool
    referal: Optional[str]
    effect: Optional[str]
    tune_id: Optional[str]
    god_mod_text: Optional[str]
    category: Optional[str]
    gender: Optional[str]
    count_video_generations: int
    referral_count: int
    reward_generations: int
    referral_purchases: int
    has_purchased: bool
    subscribe: Optional[date]
    maternity_payment_id: Optional[str]
    api_name: str
    
    
class UpdateUserDTO(Schema):
    tg_user_id: str
    count_generations: Optional[int] = None
    count_video_generations: Optional[int] = None
    is_learn_model: Optional[bool] = None
    god_mod: Optional[bool] = None
    referal: Optional[str] = None
    effect: Optional[str] = None
    tune_id: Optional[str] = None
    god_mod_text: Optional[str] = None
    category: Optional[str] = None
    gender: Optional[str] = None
    photo_from_photo: Optional[bool] = None
    subscribe: Optional[date] = None
    maternity_payment_id: Optional[str] = None


class CreateUserDTO(Schema):
    tg_user_id: str
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    last_activity: Optional[datetime] = now()
    has_purchased: Optional[bool] = False


class PaymentNotificationDTO(Schema):
    out_summ: float
    out_sum: float
    inv_id: int
    inv_id2: int
    crc: str
    signature_value: str
    payment_method: str
    inc_sum: float
    inc_curr_label: str
    is_test: bool
    email: str
    fee: float
