from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from fastapi_contrib.conf import settings


class StateRequestIDMiddleware(BaseHTTPMiddleware):

    @property
    def request_id_header_name(self) -> str:
        return settings.request_id_header

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        request_id = request.headers.get(self.request_id_header_name)
        request.state.request_id = request_id
        response = await call_next(request)
        return response
