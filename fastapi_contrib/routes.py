from typing import Callable

from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from starlette.requests import Request
from starlette.responses import Response

from fastapi_contrib.common.responses import UJSONResponse


class ValidationErrorLoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except RequestValidationError as exc:
                body = await request.body()
                if not body:
                    status_code = 400
                    data = {
                        "code": status_code,
                        "detail": "Empty body for this request is not valid.",
                        "fields": [],
                    }
                    return UJSONResponse(data, status_code=status_code)
                else:
                    raise exc

        return custom_route_handler
