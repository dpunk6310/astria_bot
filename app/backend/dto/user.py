from typing import Optional 

from ninja import Schema


class UserDTO(Schema):
    tg_user_id: str
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    

class CreateUserDTO(Schema):
    user: UserDTO
    