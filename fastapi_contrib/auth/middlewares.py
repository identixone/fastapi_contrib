from starlette.middleware.authentication import (
    AuthenticationMiddleware as BaseAuthenticationMiddleware,
)
from starlette.requests import HTTPConnection

from fastapi_contrib.common.responses import UJSONResponse


class AuthenticationMiddleware(BaseAuthenticationMiddleware):
    """
    Own Authentication Middleware based on Starlette's default one.

    Use instance of this class as a first argument to `add_middleware` func:

    .. code-block:: python

        app = FastAPI()

        @app.on_event('startup')
        async def startup():
            app.add_middleware(AuthenticationMiddleware, backend=AuthBackend())

    """
    @staticmethod
    def default_on_error(
        conn: HTTPConnection,
        exc: Exception
    ) -> UJSONResponse:
        """
        Overriden method just to make sure we return response in our format.

        :param conn: HTTPConnection of the current request-response cycle
        :param exc: Any exception that could have been raised
        :return: UJSONResponse with error data as dict and 403 status code
        """
        return UJSONResponse(
            {"code": 403, "detail": "Forbidden.", "fields": []},
            status_code=403,
        )
