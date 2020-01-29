#!/usr/bin/env python
# -*- coding: utf-8 -*-
import enum
import json
from typing import Optional, Set
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, Body, Query
from pydantic import (
    BaseModel,
    ValidationError,
    constr,
    validator,
    PydanticValueError,
)
from pydantic.error_wrappers import ErrorWrapper
from starlette.requests import Request

from fastapi_contrib.exceptions import (
    HTTPException,
    NotFoundError,
    InternalServerError,
)
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
    raise InternalServerError()


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


class CustomValidatorError(PydanticValueError):
    error_code = 4
    code = f"error_code.{error_code}"
    msg_template = "custom message!"


class CustomValidationItem(BaseModel):
    field1: str
    field2: int
    field3: float = 42.0

    @validator("field1")
    def field1_must_contain_42(cls, v):
        if "42" not in v:
            raise ValueError("must contain a 42")
        return v

    @validator("field2")
    def field2_must_contain_42(cls, v):
        if v != 42:
            raise CustomValidatorError()
        return v


class MultipleChoiceModel(BaseModel):
    multi: Set[Kind] = [e.value for e in Kind]


class MultipleIntModel(BaseModel):
    integers: Optional[Set[int]] = None


@app.post("/pydantic/exception/multipleint/")
async def pydantic_exc_mul_int(
    request: Request, serializer: MultipleIntModel
) -> dict:
    return serializer.dict()


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


@app.post("/pydantic/exception/multiplechoice/")
async def pydantic_exc_mul_choice(serializer: MultipleChoiceModel) -> dict:
    return serializer.dict()


@app.post("/pydantic/exception/customvalidation/")
async def pydantic_exception_custom_validation(item: CustomValidationItem):
    return {"item": item.dict()}


@app.get("/pydantic/exception/custom404/")
async def pydantic_exception_custom_404():
    raise NotFoundError(detail="this is really bad")


@app.get("/pydantic/exception/invalidquery/")
async def pydantic_exception_invalid_query(q: int = Query(...)):
    return {"q": q}


def test_exception_handler_invalid_query():
    with TestClient(app) as client:
        response = client.get(
            "/pydantic/exception/invalidquery/", params={"q": "$"}
        )
        assert response.status_code == 400
        response = response.json()
        assert response["error_codes"] == [400]
        assert response["message"] == "Validation error."
        assert response["fields"] == [
            {
                "name": "q",
                "message": "Value is not a valid integer.",
                "error_code": 400,
            }
        ]


def test_exception_handler_starlettehttpexception_404():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 404
        response = response.json()
        assert response["error_codes"] == [404]
        assert response["fields"] == []


def test_exception_handler_customhttpexception_404():
    with TestClient(app) as client:
        response = client.get("/pydantic/exception/custom404/")
        assert response.status_code == 404
        response = response.json()
        assert response["error_codes"] == [404]
        assert response["message"] == "this is really bad"
        assert response["fields"] == []


def test_exception_handler_500():
    with TestClient(app) as client:
        response = client.get("/500/")
        assert response.status_code == 500
        response = response.json()
        assert response["error_codes"] == [500]
        assert response["message"] == "Internal Server Error."
        assert response["fields"] == []


def test_exception_handler_starlettehttpexception_custom():
    with TestClient(app) as client:
        response = client.get("/starlette/exception/")
        assert response.status_code == 400
        response = response.json()
        assert response["error_codes"] == [400]
        assert response["message"] == "required."
        assert response["fields"] == [{"field": "value"}]


def test_exception_handler_when_regex_invalid():
    with TestClient(app) as client:
        response = client.post(
            "/pydantic/exception/regexp/", json={"name": "$$$"}
        )
        assert response.status_code == 400
        response = response.json()
        assert response["error_codes"] == [400]
        assert response["message"] == "Validation error."
        assert response["fields"] == [
            {
                "message": "Provided value doesn't match valid format.",
                "name": "name",
                "error_code": 400,
            }
        ]


def test_exception_handler_when_choice_invalid():
    with TestClient(app) as client:
        response = client.post(
            "/pydantic/exception/choice/", json={"kind": "d"}
        )
        assert response.status_code == 400
        response = response.json()
        assert response["error_codes"] == [400]
        assert response["message"] == "Validation error."
        assert response["fields"] == [
            {
                "message": "One or more values provided are not valid.",
                "name": "kind",
                "error_code": 400,
            }
        ]


def test_exception_handler_when_one_of_multi_choice_invalid():
    with TestClient(app) as client:
        response = client.post(
            "/pydantic/exception/multiplechoice/", json={"multi": ["d", "a"]}
        )
        assert response.status_code == 400
        response = response.json()
        assert response["error_codes"] == [400]
        assert response["message"] == "Validation error."
        assert response["fields"] == [
            {
                "message": "One or more values provided are not valid.",
                "name": "multi",
                "error_code": 400,
            }
        ]


def test_exception_handler_when_choice_default_and_received_invalid():
    with TestClient(app) as client:
        response = client.post(
            "/pydantic/exception/duplicate/", json={"kind": "d"}
        )
        assert response.status_code == 400
        response = response.json()
        assert response["error_codes"] == [400]
        assert response["message"] == "Validation error."
        assert response["fields"] == [
            {
                "message": "One or more values provided are not valid.",
                "name": "kind",
                "error_code": 400,
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
        assert response["error_codes"] == [400]
        assert response["message"] == "Validation error."
        assert response["fields"] == [
            {
                "message": "One or more values provided are not valid.",
                "name": "kind",
                "error_code": 400,
            },
            {
                "message": "Value is not a valid integer.",
                "name": "temp",
                "error_code": 400,
            },
        ]


def test_exception_handler_with_custom_field_validator():
    with TestClient(app) as client:
        response = client.post(
            "/pydantic/exception/customvalidation/",
            json={"field1": "d", "field2": 1},
        )
        assert response.status_code == 400
        response = response.json()
        assert response == {
            "error_codes": [400, 4],
            "message": "Validation error.",
            "fields": [
                {
                    "name": "field1",
                    "message": "Must contain a 42.",
                    "error_code": 400,
                },
                {
                    "name": "field2",
                    "message": "Custom message!",
                    "error_code": 4,
                },
            ],
        }


def test_exception_handler_with_list_str_instead_of_ints():
    with TestClient(app) as client:
        response = client.post(
            "/pydantic/exception/multipleint/", json={"integers": ["d"]}
        )
        assert response.status_code == 400
        response = response.json()
        assert response == {
            "error_codes": [400],
            "message": "Validation error.",
            "fields": [
                {
                    "name": "integers",
                    "message": "Value is not a valid integer.",
                    "error_code": 400,
                }
            ],
        }


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
    exc = Exception("World: ")
    exc.raw_errors = [
        ErrorWrapper(loc=("hello", "world"), exc=Exception("World!"))
    ]
    error = ValidationError(
        [ErrorWrapper(loc=("hello", "world"), exc=exc)], model=Item
    )
    raw_response = await validation_exception_handler(request, error)
    response = json.loads(raw_response.body.decode("utf-8"))

    assert response["error_codes"] == [400]
    assert response["message"] == "Validation error."
    assert response["fields"] == [
        {"name": "hello", "message": "World!", "error_code": 400}
    ]

    exc = Exception()
    error = ValidationError(
        [ErrorWrapper(loc=("body", "world22"), exc=exc)], model=Item
    )
    raw_response = await validation_exception_handler(request, error)
    response = json.loads(raw_response.body.decode("utf-8"))

    assert response["error_codes"] == [400]
    assert response["message"] == "Validation error."
    assert response["fields"] == [
        {"name": "world22", "message": "", "error_code": 400}
    ]

    exc = Exception()
    error = ValidationError(
        [ErrorWrapper(loc=("body", "world22", "missing"), exc=exc)], model=Item
    )
    raw_response = await validation_exception_handler(request, error)
    response = json.loads(raw_response.body.decode("utf-8"))

    assert response["error_codes"] == [400]
    assert response["message"] == "Validation error."
    assert response["fields"] == [
        {"name": "__all__", "message": "", "error_code": 400}
    ]

    exc = Exception()
    error = ValidationError(
        [ErrorWrapper(loc=("data", "world22"), exc=exc)], model=Item
    )
    raw_response = await validation_exception_handler(request, error)
    response = json.loads(raw_response.body.decode("utf-8"))

    assert response["error_codes"] == [400]
    assert response["message"] == "Validation error."
    assert response["fields"] == [
        {"name": "data", "message": "", "error_code": 400}
    ]

    exc = Exception()
    error = ValidationError([ErrorWrapper(loc=("body",), exc=exc)], model=Item)
    raw_response = await validation_exception_handler(request, error)
    response = json.loads(raw_response.body.decode("utf-8"))

    assert response["error_codes"] == [400]
    assert response["message"] == "Validation error."
    assert response["fields"] == [
        {"name": "__all__", "message": "", "error_code": 400}
    ]

    exc = Exception()
    error = ValidationError([ErrorWrapper(loc=("data",), exc=exc)], model=Item)
    raw_response = await validation_exception_handler(request, error)
    response = json.loads(raw_response.body.decode("utf-8"))

    assert response["error_codes"] == [400]
    assert response["message"] == "Validation error."
    assert response["fields"] == [
        {"name": "data", "message": "", "error_code": 400}
    ]


def test_parse_error_edge_cases():
    err = MagicMock()
    err.loc = ("field",)
    err.msg = "This field contains an error."
    parsed_dict = parse_error(err, field_names=["random"], raw=True)
    assert parsed_dict["name"] == err.loc[0]
    assert parsed_dict["message"] == err.msg

    err = MagicMock()
    err.loc = ()
    err.msg = "This field contains an error."
    parsed_dict = parse_error(err, field_names=["random"], raw=True)
    assert parsed_dict["name"] == "__all__"
    assert parsed_dict["message"] == err.msg
