from starlette.middleware.authentication import (
    AuthenticationMiddleware as BaseAuthenticationMiddleware,
)
from starlette.requests import HTTPConnection

from fastapi_contrib.common.responses import UJSONResponse


class AuthenticationMiddleware(BaseAuthenticationMiddleware):
    @staticmethod
    def default_on_error(conn: HTTPConnection, exc: Exception) -> UJSONResponse:
        return UJSONResponse(
            {"code": 403, "detail": "Forbidden.", "fields": []},
            status_code=403,
        )
