#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, Body
from pydantic import BaseModel, ValidationError
from pydantic.error_wrappers import ErrorWrapper
from starlette.requests import Request

from fastapi_contrib.exceptions import HTTPException
from starlette.testclient import TestClient

from fastapi_contrib.exception_handlers import (
    setup_exception_handlers,
    parse_error,
    validation_exception_handler,
)

app = FastAPI()


@app.on_event("startup")
async def startup():
    setup_exception_handlers(app)


@app.get("/500/")
async def internal_server_error_view():
    raise RuntimeError()


@app.get("/starlette/exception/")
async def starlette_exception():
    raise HTTPException(
        status_code=400,
        detail="required",
        fields=[{"field": "value"}],
        error_code=400,
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


def test_exception_handler_500():
    with pytest.raises(RuntimeError):
        with TestClient(app) as client:
            response = client.get("/500/")
            assert response.status_code == 500
            response = response.json()
            assert response["code"] == 500
            assert response["fields"] == []


def test_exception_handler_starlettehttpexception_custom():
    with TestClient(app) as client:
        response = client.get("/starlette/exception/")
        assert response.status_code == 400
        response = response.json()
        assert response["code"] == 400
        assert response["fields"] == [{"field": "value"}]


@pytest.mark.asyncio
async def test_exception_handler_pydantic_validationerror_model():
    async def test_receive():
        return {
            "type": "http.request",
            "body": json.dumps({"id": "str", "name": []}).encode("utf-8"),
        }

    request = Request(
        {"type": "http", "method": "GET", "path": "/"}, receive=test_receive
    )
    exc = Exception()
    exc.raw_errors = [ErrorWrapper(loc=("hello", "world"), exc=Exception())]
    error = ValidationError(
        [ErrorWrapper(loc=("hello", "world"), exc=exc)], model=Item
    )
    raw_response = await validation_exception_handler(request, error)
    response = json.loads(raw_response.body.decode("utf-8"))

    assert response["code"] == 400
    assert response["detail"] == "Validation error"
    assert response["fields"] == [{"name": "hello", "message": "World: "}]

    exc = Exception()
    error = ValidationError(
        [ErrorWrapper(loc=("body", "world22"), exc=exc)], model=Item
    )
    raw_response = await validation_exception_handler(request, error)
    response = json.loads(raw_response.body.decode("utf-8"))

    assert response["code"] == 400
    assert response["detail"] == "Validation error"
    assert response["fields"] == [{"name": "world22", "message": ""}]

    exc = Exception()
    error = ValidationError(
        [ErrorWrapper(loc=("body", "world22", "missing"), exc=exc)], model=Item
    )
    raw_response = await validation_exception_handler(request, error)
    response = json.loads(raw_response.body.decode("utf-8"))

    assert response["code"] == 400
    assert response["detail"] == "Validation error"
    assert response["fields"] == [{"name": "__all__", "message": ""}]

    exc = Exception()
    error = ValidationError(
        [ErrorWrapper(loc=("data", "world22"), exc=exc)], model=Item
    )
    raw_response = await validation_exception_handler(request, error)
    response = json.loads(raw_response.body.decode("utf-8"))

    assert response["code"] == 400
    assert response["detail"] == "Validation error"
    assert response["fields"] == [{"name": "data", "message": ""}]

    exc = Exception()
    error = ValidationError(
        [ErrorWrapper(loc=("body",), exc=exc)], model=Item
    )
    raw_response = await validation_exception_handler(request, error)
    response = json.loads(raw_response.body.decode("utf-8"))

    assert response["code"] == 400
    assert response["detail"] == "Validation error"
    assert response["fields"] == [{"name": "__all__", "message": ""}]

    exc = Exception()
    error = ValidationError(
        [ErrorWrapper(loc=("data",), exc=exc)], model=Item
    )
    raw_response = await validation_exception_handler(request, error)
    response = json.loads(raw_response.body.decode("utf-8"))

    assert response["code"] == 400
    assert response["detail"] == "Validation error"
    assert response["fields"] == [{"name": "data", "message": ""}]


def test_parse_error_edge_cases():
    # TODO: this should be tested through exception raising somehow
    err = MagicMock()
    err.loc = ("field",)
    err.msg = "This field contains an error."
    parsed_dict = parse_error(err)
    assert parsed_dict == {"name": err.loc[0], "message": err.msg}

    err = MagicMock()
    err.loc = ()
    err.msg = "This field contains an error."
    parsed_dict = parse_error(err)
    assert parsed_dict == {"name": "__all__", "message": err.msg}
