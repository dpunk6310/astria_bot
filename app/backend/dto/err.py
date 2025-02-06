from ninja import Schema


class ErrorDTO(Schema):
    message: str
    err: str

class SuccessDTO(Schema):
    status: str
    message: str
