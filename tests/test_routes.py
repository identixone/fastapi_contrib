#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi import FastAPI
from pydantic import BaseModel
from starlette.testclient import TestClient

from fastapi_contrib.routes import ValidationErrorLoggingRoute

app = FastAPI()
app.router.route_class = ValidationErrorLoggingRoute


class Item(BaseModel):
    uid: int
    name: str


@app.post("/pydantic/validation/route/")
async def pydantic_exception_model(item: Item):
    return {"item": item.dict()}


def test_empty_body_caught_in_route_class_handler():
    with TestClient(app) as client:
        response = client.post("/pydantic/validation/route/")
        assert response.status_code == 400
        response = response.json()
        assert response["code"] == 400
        assert response["fields"] == []
        assert (
            response["detail"] == "Empty body for this request is not valid."
        )


def test_missing_field_not_caught_in_route_class_handler():
    with TestClient(app) as client:
        response = client.post(
            "/pydantic/validation/route/", json={"name": "name111"}
        )
        # 422 means that exception got propagated to the default exception
        # handler of FastAPI, therefore not caught by our custom route class
        assert response.status_code == 422
