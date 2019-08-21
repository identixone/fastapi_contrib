from starlette.exceptions import HTTPException as StarletteHTTPException


class NotFoundError(StarletteHTTPException):
    def __init__(self):
        detail = "Not found."
        super().__init__(status_code=404, detail=detail)
        self.error_code = 404


class BadRequestError(StarletteHTTPException):

    def __init__(self, code: int, detail=None):
        super().__init__(status_code=400, detail=detail)
        self.error_code = code
