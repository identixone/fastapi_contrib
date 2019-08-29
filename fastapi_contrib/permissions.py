from abc import ABC, abstractmethod

from starlette import status
from starlette.requests import Request

from fastapi_contrib.exceptions import HTTPException


class BasePermission(ABC):
    error_msg = "Forbidden."
    status_code = status.HTTP_403_FORBIDDEN
    error_code = status.HTTP_403_FORBIDDEN

    @abstractmethod
    def has_required_permisions(self, request: Request) -> bool:
        ...

    def __init__(self, request: Request):
        if not self.has_required_permisions(request):
            raise HTTPException(
                status_code=self.status_code,
                detail=self.error_msg,
                error_code=self.error_code
            )


class PermissionsDependency(object):

    def __init__(self, permissions_classes: list):
        self.permissions_classes = permissions_classes

    def __call__(self, request: Request):
        for permission_class in self.permissions_classes:
            permission_class(request=request)
