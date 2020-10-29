from abc import ABC, abstractmethod

from starlette import status
from starlette.requests import Request

from fastapi_contrib.exceptions import HTTPException


class BasePermission(ABC):
    """
    Abstract permission that all other Permissions must be inherited from.

    Defines basic error message, status & error codes.

    Upon initialization, calls abstract method  `has_required_permissions`
    which will be specific to concrete implementation of Permission class.

    You would write your permissions like this:

    .. code-block:: python

        class TeapotUserAgentPermission(BasePermission):

            def has_required_permissions(self, request: Request) -> bool:
                return request.headers.get('User-Agent') == "Teapot v1.0"

    """
    error_msg = "Forbidden."
    status_code = status.HTTP_403_FORBIDDEN
    error_code = status.HTTP_403_FORBIDDEN

    @abstractmethod
    def has_required_permissions(self, request: Request) -> bool:
        ...

    def __init__(self, request: Request):
        if not self.has_required_permissions(request):
            raise HTTPException(
                status_code=self.status_code,
                detail=self.error_msg,
                error_code=self.error_code
            )


class PermissionsDependency(object):
    """
    Permission dependency that is used to define and check all the permission
    classes from one place inside route definition.

    Use it as an argument to FastAPI's `Depends` as follows:

    .. code-block:: python

        app = FastAPI()

        @app.get(
            "/teapot/",
            dependencies=[Depends(
                PermissionsDependency([TeapotUserAgentPermission]))]
        )
        async def teapot() -> dict:
            return {"teapot": True}
    """

    def __init__(self, permissions_classes: list):
        self.permissions_classes = permissions_classes

    def __call__(self, request: Request):
        for permission_class in self.permissions_classes:
            permission_class(request=request)
