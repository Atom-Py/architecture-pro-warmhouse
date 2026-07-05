from msgspec import Struct


class ErrorResponse(Struct, gc=False):
    code: str
    message: str
