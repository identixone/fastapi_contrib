#!/usr/bin/env python
# -*- coding: utf-8 -*-
import enum
import json
from typing import Optional
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, Body, Form
from pydantic import BaseModel, ValidationError, constr
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


@app.get("/404/")
async def not_found_error_view():
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


class RegexpItem(BaseModel):
    name: constr(regex=r"^[a-z]$")


class Kind(str, enum.Enum):
    a = "a"
    b = "b"
    c = "c"


class ChoiceItem(BaseModel):
    kind: Kind


@app.post("/pydantic/exception/model/")
async def pydantic_exception_model(item: Item):
    return {"item": item.dict()}


@app.post("/pydantic/exception/regexp/")
async def pydantic_exception_regexp(item: RegexpItem):
    return {"item": item.dict()}


@app.post("/pydantic/exception/choice/")
async def pydantic_exception_choice(item: ChoiceItem):
    return {"item": item.dict()}


@app.post("/pydantic/exception/duplicate/")
async def pydantic_exception_duplicate(
    kind: Optional[Kind] = Body(default=Kind.a), temp: int = Body(default=1)
):
    return {"kind": kind}


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


def test_exception_handler_when_regex_invalid():
    with TestClient(app) as client:
        response = client.post(
            "/pydantic/exception/regexp/", json={"name": "$$$"}
        )
        assert response.status_code == 400
        response = response.json()
        assert response["code"] == 400
        assert response["fields"] == [
            {
                "message": "Provided value doesn't match valid format.",
                "name": "name",
            }
        ]


def test_exception_handler_when_choice_invalid():
    with TestClient(app) as client:
        response = client.post(
            "/pydantic/exception/choice/", json={"kind": "d"}
        )
        assert response.status_code == 400
        response = response.json()
        assert response["code"] == 400
        assert response["fields"] == [
            {
                "message": "One or more values provided are not valid.",
                "name": "kind",
            }
        ]


def test_exception_handler_when_choice_default_and_received_invalid():
    with TestClient(app) as client:
        response = client.post(
            "/pydantic/exception/duplicate/", json={"kind": "d"}
        )
        assert response.status_code == 400
        response = response.json()
        assert response["code"] == 400
        assert response["fields"] == [
            {
                "message": "One or more values provided are not valid.",
                "name": "kind",
            }
        ]

        response = client.post("/pydantic/exception/duplicate/")
        assert response.status_code == 200
        response = response.json()
        assert response["kind"] == Kind.a

        response = client.post(
            "/pydantic/exception/duplicate/", json={"kind": "d", "temp": "$"}
        )
        assert response.status_code == 400
        response = response.json()
        assert response["code"] == 400
        assert response["fields"] == [
            {
                "message": "One or more values provided are not valid.",
                "name": "kind",
            },
            {
                "message": "Value is not a valid integer",
                "name": "temp"
            },
        ]


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
    error = ValidationError([ErrorWrapper(loc=("body",), exc=exc)], model=Item)
    raw_response = await validation_exception_handler(request, error)
    response = json.loads(raw_response.body.decode("utf-8"))

    assert response["code"] == 400
    assert response["detail"] == "Validation error"
    assert response["fields"] == [{"name": "__all__", "message": ""}]

    exc = Exception()
    error = ValidationError([ErrorWrapper(loc=("data",), exc=exc)], model=Item)
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
    parsed_dict = parse_error(err, field_names=["random"])
    assert parsed_dict == {"name": err.loc[0], "message": err.msg}

    err = MagicMock()
    err.loc = ()
    err.msg = "This field contains an error."
    parsed_dict = parse_error(err, field_names=["random"])
    assert parsed_dict == {"name": "__all__", "message": err.msg}
