from typing import Any

from starlette.exceptions import HTTPException as StarletteHTTPException


class HTTPException(StarletteHTTPException):
    def __init__(
        self,
        status_code: int,
        error_code: int,
        detail: Any = None
    ) -> None:
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code


class BadRequestError(HTTPException):

    def __init__(self, error_code: int, detail: Any):
        super().__init__(error_code=error_code, status_code=400, detail=detail)


class ForbiddenError(HTTPException):

    def __init__(self, error_code: int = 403, detail: Any = "Forbidden."):
        super().__init__(error_code=error_code, status_code=403, detail=detail)


class NotFoundError(HTTPException):

    def __init__(self, error_code: int = 404, detail: Any = "Not found."):
        super().__init__(error_code=error_code, status_code=404, detail=detail)
