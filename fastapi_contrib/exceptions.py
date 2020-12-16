from typing import Any, List, Dict

from starlette.exceptions import HTTPException as StarletteHTTPException


class HTTPException(StarletteHTTPException):
    def __init__(
        self,
        status_code: int,
        error_code: int,
        detail: Any = None,
        fields: List[Dict] = None,
    ) -> None:
        """
        Generic HTTP Exception with support for custom status & error codes.

        :param status_code: HTTP status code of the response
        :param error_code: Custom error code, unique throughout the app
        :param detail: detailed message of the error
        :param fields: list of dicts with key as field and value as message
        """
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.fields = fields or []


class BadRequestError(HTTPException):
    def __init__(
        self, error_code: int, detail: Any, fields: List[Dict] = None
    ):
        """
        Generic Bad Request HTTP Exception with support for custom error code.

        :param error_code: Custom error code, unique throughout the app
        :param detail: detailed message of the error
        """
        super().__init__(
            error_code=error_code,
            status_code=400,
            detail=detail,
            fields=fields,
        )


class UnauthorizedError(HTTPException):
    def __init__(
        self,
        error_code: int = 401,
        detail: Any = "Unauthorized.",
        fields: List[Dict] = None,
    ):
        """
        Generic Unauthorized HTTP Exception with support for custom error code.

        :param error_code: Custom error code, unique throughout the app
        :param detail: detailed message of the error
        """
        super().__init__(
            error_code=error_code,
            status_code=401,
            detail=detail,
            fields=fields,
        )


class ForbiddenError(HTTPException):
    def __init__(
        self,
        error_code: int = 403,
        detail: Any = "Forbidden.",
        fields: List[Dict] = None,
    ):
        """
        Generic Forbidden HTTP Exception with support for custom error code.

        :param error_code: Custom error code, unique throughout the app
        :param detail: detailed message of the error
        """
        super().__init__(
            error_code=error_code,
            status_code=403,
            detail=detail,
            fields=fields,
        )


class NotFoundError(HTTPException):
    def __init__(
        self,
        error_code: int = 404,
        detail: Any = "Not found.",
        fields: List[Dict] = None,
    ):
        """
        Generic 404 Not Found HTTP Exception with support for custom error code

        :param error_code: Custom error code, unique throughout the app
        :param detail: detailed message of the error
        """
        super().__init__(
            error_code=error_code,
            status_code=404,
            detail=detail,
            fields=fields,
        )


class InternalServerError(HTTPException):
    def __init__(
        self,
        error_code: int = 500,
        detail: Any = "Internal Server Error.",
        fields: List[Dict] = None,
    ):
        """
        Generic Internal Server Error with support for custom error code.

        :param error_code: Custom error code, unique throughout the app
        :param detail: detailed message of the error
        """
        super().__init__(
            error_code=error_code,
            status_code=500,
            detail=detail,
            fields=fields,
        )
