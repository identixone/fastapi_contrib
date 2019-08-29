#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi import FastAPI, Body
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.testclient import TestClient

from fastapi_contrib.exception_handlers import setup_exception_handlers


app = FastAPI()


@app.on_event("startup")
async def startup():
    setup_exception_handlers(app)


@app.get("/starlette/exception/")
async def starlette_exception():
    raise StarletteHTTPException(status_code=400, detail="required")


@app.post("/pydantic/exception/")
async def pydantic_exception(item: str = Body(...)):
    return {"item": item}


class Item(BaseModel):
    uid: int
    name: str


@app.post("/pydantic/exception/model/")
async def pydantic_exception_model(item: Item):
    return {"item": item.dict()}


def test_exception_handler_starlettehttpexception_404():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 404
        response = response.json()
        assert response["code"] == 404
        assert response["fields"] == []


def test_exception_handler_starlettehttpexception_custom():
    with TestClient(app) as client:
        response = client.get("/starlette/exception/")
        assert response.status_code == 400
        response = response.json()
        assert response["code"] == 400
        assert response["fields"] == []


def test_exception_handler_pydantic_validationerror():
    with TestClient(app) as client:
        response = client.post("/pydantic/exception/")
        assert response.status_code == 400
        response = response.json()
        assert response["code"] == 400
        assert "item" in response["fields"][0].values()


def test_exception_handler_pydantic_validationerror_model():
    with TestClient(app) as client:
        response = client.post("/pydantic/exception/model/")
        assert response.status_code == 400
        response = response.json()
        assert response["code"] == 400
        assert "item" in response["fields"][0].values()

        response = client.post(
            "/pydantic/exception/model/",
            json={"id": "str", "name": []}
        )
        assert response.status_code == 400
        response = response.json()
        assert response["code"] == 400
