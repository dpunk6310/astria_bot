from typing import Optional, Any

from ninja import Schema


class UserDTO(Schema):
    tg_user_id: str
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    
    
class UpdateUserDTO(Schema):
    tg_user_id: str
    count_generations: int
    

class CreateUserDTO(Schema):
    user: UserDTO


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
