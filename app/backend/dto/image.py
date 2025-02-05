from ninja import Schema


class ImageDTO(Schema):
    tg_user_id: str
    path: str
    

class CreateImageDTO(Schema):
    image: ImageDTO
    