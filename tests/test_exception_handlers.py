#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest.mock import MagicMock

from fastapi import FastAPI, Body
from pydantic import BaseModel
from fastapi_contrib.exceptions import HTTPException
from starlette.testclient import TestClient

from fastapi_contrib.exception_handlers import (
    setup_exception_handlers, parse_raw_error)

app = FastAPI()


@app.on_event("startup")
async def startup():
    setup_exception_handlers(app)


@app.get("/starlette/exception/")
async def starlette_exception():
    raise HTTPException(
        status_code=400,
        detail="required",
        fields=[{"field": "value"}],
        error_code=400
    )


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
        assert response["fields"] == [{'field': 'value'}]


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


def test_parse_raw_error_edge_cases():
    # TODO: this should be tested through exception raising somehow
    err = MagicMock()
    err.loc = ("field",)
    err.msg = "This field contains an error."
    parsed_dict = parse_raw_error(err)
    assert parsed_dict == {"name": err.loc[0], "message": err.msg}

    err = MagicMock()
    err.loc = ()
    err.msg = "This field contains an error."
    parsed_dict = parse_raw_error(err)
    assert parsed_dict == {"name": "__all__", "message": err.msg}
