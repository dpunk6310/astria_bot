from ninja import Schema


class TGImageDTO(Schema):
    id: int
    tg_user_id: str
    tg_hash: str


class CreateTGImageDTO(Schema):
    image: TGImageDTO
