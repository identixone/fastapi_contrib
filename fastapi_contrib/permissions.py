from abc import ABC, abstractmethod
from fastapi.exceptions import HTTPException
from starlette.requests import Request


class BasePermission(ABC):
    error_msg = None
    status_code = None

    @abstractmethod
    def has_required_permisions(self, request: Request) -> bool:
        ...

    def __init__(self, request: Request):
        if not self.has_required_permisions(request):
            raise HTTPException(
                status_code=self.status_code,
                detail=self.error_msg
            )


class PermissionsDependency(object):

    def __init__(self, permissions_classes: list):
        self.permissions_classes = permissions_classes

    def __call__(self, request: Request):
        for permission_class in self.permissions_classes:
            permission_class(request=request)
