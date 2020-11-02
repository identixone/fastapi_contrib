from starlette.requests import Request
from starlette import status

from fastapi_contrib.permissions import BasePermission


class IsAuthenticated(BasePermission):
    """
    Permission that checks if the user has been authenticated (by middleware)

    Use it as an argument to `PermissionsDependency` as follows:

    .. code-block:: python

        app = FastAPI()

        @app.get(
            "/user/",
            dependencies=[Depends(PermissionsDependency([IsAuthenticated]))]
        )
        async def user(request: Request) -> dict:
            return request.scope["user"].dict()

    """
    error_msg = "Not authenticated."
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = status.HTTP_401_UNAUTHORIZED

    def has_required_permissions(self, request: Request) -> bool:
        return request.user is not None
