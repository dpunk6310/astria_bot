from ninja import Schema


class UpdatePromoDTO(Schema):
    code: str
    tg_user_id: str
    status: bool
