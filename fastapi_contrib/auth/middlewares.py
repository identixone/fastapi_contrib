from starlette.middleware.authentication import (
    AuthenticationMiddleware as BaseAuthenticationMiddleware,
)
from starlette.requests import HTTPConnection
from starlette.responses import PlainTextResponse, Response


class AuthenticationMiddleware(BaseAuthenticationMiddleware):
    @staticmethod
    def default_on_error(conn: HTTPConnection, exc: Exception) -> Response:
        return PlainTextResponse(str(exc), status_code=403)
