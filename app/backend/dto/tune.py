from ninja import Schema


class CreateTuneDTO(Schema):
    tg_user_id: str
    tune_id: str
    gender: str


class TuneListDTO(Schema):
    tg_user_id: str
    tune_id: str
    gender: str