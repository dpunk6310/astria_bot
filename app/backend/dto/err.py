from ninja import Schema


class ErrorDTO(Schema):
    message: str
    err: str