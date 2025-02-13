from typing import List

from ninja import Schema


class PromtDTO(Schema):
    text: str


class CategoryDTO(Schema):
    name: str
    slug: str
    gender: str
    promts: List[PromtDTO]