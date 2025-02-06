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
    OutSum: Any
    InvId: Any
    SignatureValue: Any
