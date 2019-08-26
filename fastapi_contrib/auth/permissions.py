from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from fastapi_contrib.permissions import BasePermission


class IsAuthenticated(BasePermission):
    error_msg = "Not authenticated"
    status_code = HTTP_401_UNAUTHORIZED

    def has_required_permisions(self, request: Request) -> bool:
        return request.user is not None
