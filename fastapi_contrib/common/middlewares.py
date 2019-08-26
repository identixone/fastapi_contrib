from starlette.middleware.base import BaseHTTPMiddleware

from fastapi_contrib.conf import settings


class StateRequestIDMiddleware(BaseHTTPMiddleware):

    @property
    def request_id_header_name(self):
        return settings.request_id_header

    async def dispatch(self, request, call_next):
        request_id = request.headers.get(self.request_id_header_name)
        request.state.request_id = request_id
        response = await call_next(request)
        return response
