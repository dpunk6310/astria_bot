from typing import Optional

from ninja import Schema


class PriceListDTO(Schema):
    price: str
    count: int
    learn_model: bool
    sale: Optional[str]
    count_video: int
