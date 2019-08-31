#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi import FastAPI
from starlette.requests import Request
from starlette.testclient import TestClient
from unittest.mock import patch

from fastapi_contrib.auth.backends import AuthBackend
from fastapi_contrib.auth.middlewares import AuthenticationMiddleware
from fastapi_contrib.auth.utils import get_token_model, get_user_model
from tests.utils import AsyncMock

app = FastAPI()
app.add_middleware(AuthenticationMiddleware, backend=AuthBackend())


Token = get_token_model()
User = get_user_model()


@app.get("/me/")
async def index(request: Request):
    user = request.scope["user"]
    str_user_or_none = user.username if user else None
    return {"username": str_user_or_none}


def test_user_not_logged_in():
    with TestClient(app) as client:
        response = client.get("/me/")
        assert response.status_code == 200
        response = response.json()
        assert response["username"] is None


def test_invalid_auth_header():
    with TestClient(app) as client:
        response = client.get("/me/", headers={"Authorization": f"toookennn"})
        assert response.status_code == 403
        response = response.json()
        assert response["code"] == 403
        assert response["fields"] == []


def test_invalid_auth_header_keyword():
    with TestClient(app) as client:
        response = client.get("/me/", headers={"Authorization": f"Bearer asd"})
        assert response.status_code == 403
        response = response.json()
        assert response["code"] == 403
        assert response["fields"] == []


@patch(
    "fastapi_contrib.auth.models.User.get",
    new=AsyncMock(return_value=User(username="u")),
)
@patch(
    "fastapi_contrib.auth.models.Token.get",
    new=AsyncMock(return_value=None),
)
def test_invalid_token():
    with TestClient(app) as client:
        response = client.get("/me/", headers={"Authorization": f"Token t"})
        assert response.status_code == 200
        response = response.json()
        assert response["username"] is None


@patch(
    "fastapi_contrib.auth.models.User.get",
    new=AsyncMock(return_value=None),
)
@patch(
    "fastapi_contrib.auth.models.Token.get",
    new=AsyncMock(return_value=Token()),
)
def test_invalid_user():
    with TestClient(app) as client:
        response = client.get("/me/", headers={"Authorization": f"Token t"})
        assert response.status_code == 200
        response = response.json()
        assert response["username"] is None


@patch(
    "fastapi_contrib.auth.models.User.get",
    new=AsyncMock(return_value=User(username="u")),
)
@patch(
    "fastapi_contrib.auth.models.Token.get",
    new=AsyncMock(return_value=Token()),
)
def test_user_logged_in():
    with TestClient(app) as client:
        response = client.get(
            "/me/", headers={"Authorization": f"Token t"}
        )
        assert response.status_code == 200
        response = response.json()
        assert response["username"] == "u"
