from ninja import Schema


class CreateTuneDTO(Schema):
    tg_user_id: str
    tune_id: str
    gender: str
    name: str
    api_name: str


class TuneListDTO(Schema):
    tg_user_id: str
    tune_id: str
    gender: str
    name: str
    api_name: str