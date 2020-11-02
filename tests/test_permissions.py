#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from fastapi_contrib.exceptions import HTTPException
from fastapi_contrib.permissions import BasePermission, PermissionsDependency

from starlette import status
from starlette.requests import Request


@pytest.fixture
def dumb_request():
    return Request({"type": "http", "method": "GET", "path": "/"})


def test_base_permission_instance(dumb_request):
    with pytest.raises(TypeError):
        BasePermission(request=dumb_request)


def test_base_permission_has_required_permission(dumb_request):
    class NewPermission(BasePermission):
        pass

    with pytest.raises(TypeError):
        NewPermission(request=dumb_request)

    class NewPermission(BasePermission):

        def has_required_permissions(self, request: Request) -> bool:
            return super().has_required_permissions(request=request)

    with pytest.raises(HTTPException):
        NewPermission(request=dumb_request)


def test_base_permission_no_permission_raises_403(dumb_request):
    class FailPermission(BasePermission):

        def has_required_permissions(self, request: Request) -> bool:
            return False

    with pytest.raises(HTTPException) as excinfo:
        FailPermission(request=dumb_request)

    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
    assert excinfo.value.detail == "Forbidden."


def test_base_permission_has_permission_not_raises(dumb_request):
    class AllowPermission(BasePermission):

        def has_required_permissions(self, request: Request) -> bool:
            return True

    permission = AllowPermission(request=dumb_request)
    assert isinstance(permission, AllowPermission)
    assert isinstance(permission, BasePermission)


def test_permissions_dependency_as_class(dumb_request):
    class FailPermission(BasePermission):

        def has_required_permissions(self, request: Request) -> bool:
            return False

    class AllowPermission(BasePermission):

        def has_required_permissions(self, request: Request) -> bool:
            return True

    dependency = PermissionsDependency(permissions_classes=[AllowPermission])
    dependency(request=dumb_request)

    dependency = PermissionsDependency(
        permissions_classes=[AllowPermission, FailPermission])

    with pytest.raises(HTTPException) as excinfo:
        dependency(request=dumb_request)

    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
    assert excinfo.value.detail == "Forbidden."
