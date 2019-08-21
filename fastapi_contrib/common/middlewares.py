from starlette.middleware.base import BaseHTTPMiddleware


class StateRequestIDMiddleware(BaseHTTPMiddleware):

    @property
    def request_id_header_name(self):
        return "X-RequestID"

    async def dispatch(self, request, call_next):
        request_id = request.headers.get(self.request_id_header_name)
        request.state.request_id = request_id
        response = await call_next(request)
        return response
