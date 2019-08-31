from starlette.middleware.authentication import (
    AuthenticationMiddleware as BaseAuthenticationMiddleware,
)
from starlette.requests import HTTPConnection
from starlette.responses import Response

from fastapi_contrib.common.responses import UJSONResponse


class AuthenticationMiddleware(BaseAuthenticationMiddleware):
    @staticmethod
    def default_on_error(conn: HTTPConnection, exc: Exception) -> Response:
        return UJSONResponse(
            {"code": 403, "detail": "Forbidden.", "fields": []},
            status_code=403,
        )
