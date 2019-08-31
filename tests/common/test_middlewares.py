#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid

from fastapi import FastAPI
from starlette.requests import Request
from starlette.testclient import TestClient

from fastapi_contrib.common.middlewares import StateRequestIDMiddleware
from fastapi_contrib.conf import settings

app = FastAPI()

app.add_middleware(StateRequestIDMiddleware)


@app.get("/")
async def index(request: Request):
    return {"request_id": request.state.request_id}


def test_request_id_not_in_state():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        response = response.json()
        assert response["request_id"] is None


def test_request_id_in_state():
    with TestClient(app) as client:
        request_id = str(uuid.uuid4())
        response = client.get(
            "/", headers={settings.request_id_header: request_id}
        )
        assert response.status_code == 200
        response = response.json()
        assert response["request_id"] == request_id
