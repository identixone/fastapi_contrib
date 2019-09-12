#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import patch

from fastapi import FastAPI, Depends
from starlette.requests import Request
from starlette.testclient import TestClient

from fastapi_contrib.auth.backends import AuthBackend
from fastapi_contrib.auth.middlewares import AuthenticationMiddleware
from fastapi_contrib.auth.permissions import IsAuthenticated
from fastapi_contrib.auth.utils import get_token_model, get_user_model
from fastapi_contrib.exception_handlers import setup_exception_handlers
from fastapi_contrib.permissions import PermissionsDependency
from tests.utils import AsyncMock

app = FastAPI()
app.add_middleware(AuthenticationMiddleware, backend=AuthBackend())

Token = get_token_model()
User = get_user_model()


@app.on_event("startup")
async def startup():
    setup_exception_handlers(app)


@app.get(
    "/authed/",
    dependencies=[Depends(PermissionsDependency([IsAuthenticated]))],
)
def authed(request: Request):
    return {"username": request.scope["user"].username}


@patch(
    "fastapi_contrib.auth.models.User.get",
    new=AsyncMock(return_value=User(username="u")),
)
@patch(
    "fastapi_contrib.auth.models.Token.get",
    new=AsyncMock(return_value=Token()),
)
def test_has_auth_permission():
    with TestClient(app) as client:
        response = client.get(
            "/authed/", headers={"Authorization": f"Token t"}
        )
        assert response.status_code == 200
        response = response.json()
        assert response["username"] == "u"


@patch(
    "fastapi_contrib.auth.models.User.get", new=AsyncMock(return_value=None)
)
@patch(
    "fastapi_contrib.auth.models.Token.get",
    new=AsyncMock(return_value=Token()),
)
def test_doesnt_have_auth_permission():
    with TestClient(app) as client:
        response = client.get(
            "/authed/", headers={"Authorization": f"Token t"}
        )
        assert response.status_code == 401
        response = response.json()
        assert response == {
            "code": 401,
            "detail": "Not authenticated.",
            "fields": [],
        }
