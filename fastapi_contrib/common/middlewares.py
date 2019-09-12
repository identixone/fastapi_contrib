from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from fastapi_contrib.conf import settings


class StateRequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to store Request ID headers value inside request's state object.

    Use this class as a first argument to `add_middleware` func:

    .. code-block:: python

        app = FastAPI()

        @app.on_event('startup')
        async def startup():
            app.add_middleware(StateRequestIDMiddleware)

    """

    @property
    def request_id_header_name(self) -> str:
        """
        Gets the name of Request ID header from the project settings.
        :return: string with Request ID header name
        """
        return settings.request_id_header

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """
        Get header from request and save it in request's state for future use.
        :param request: current Request instance
        :param call_next: next callable in list
        :return: response
        """
        request_id = request.headers.get(self.request_id_header_name)
        request.state.request_id = request_id
        response = await call_next(request)
        return response
