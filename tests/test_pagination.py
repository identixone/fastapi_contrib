#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from fastapi import FastAPI, Depends
from starlette.requests import Request
from starlette.testclient import TestClient

from fastapi_contrib.db.models import MongoDBTimeStampedModel
from fastapi_contrib.serializers.common import ModelSerializer
from fastapi_contrib.pagination import Pagination

from tests.mock import MongoDBMock
from tests.utils import override_settings

app = FastAPI()
app.mongodb = MongoDBMock()


class Model(MongoDBTimeStampedModel):
    class Meta:
        collection = "collection"


class TestSerializer(ModelSerializer):
    class Meta:
        model = Model


@app.get("/hallo/pagination/")
async def hallo_pagination(pagination: Pagination = Depends()):
    resp = await pagination.paginate(serializer_class=TestSerializer)
    return resp


@override_settings(fastapi_app="tests.db.test_serializers.app")
def test_paginate_no_filters():
    with TestClient(app) as client:
        response = client.get("/hallo/pagination/")
        assert response.status_code == 200
        response = response.json()
        assert response["count"] == 1


@override_settings(fastapi_app="tests.db.test_serializers.app")
def test_paginate_zero_offset_zero_limit2():
    with TestClient(app) as client:
        response = client.get("/hallo/pagination/?limit=0&offset=0")
        assert response.status_code == 422


@override_settings(fastapi_app="tests.db.test_serializers.app")
def test_custom_pagination_no_filters():

    class CustomPagination(Pagination):
        default_offset = 90
        default_limit = 1
        max_offset = 100
        max_limit = 2000

    @app.get("/hallo2/pagination2/")
    async def hallo2_pagination2(pagination: CustomPagination = Depends()):
        resp = await pagination.paginate(serializer_class=TestSerializer)
        return resp

    with TestClient(app) as client:
        response = client.get("/hallo2/pagination2/")
        assert response.status_code == 200


@override_settings(fastapi_app="tests.db.test_serializers.app")
def test_custom_pagination_correct_filters():

    class CustomPagination2(Pagination):
        default_offset = 90
        default_limit = 1
        max_offset = 100
        max_limit = 2000

    @app.get("/hallo3/pagination3/")
    async def hallo3_pagination3(pagination: CustomPagination2 = Depends()):
        resp = await pagination.paginate(serializer_class=TestSerializer)
        return resp

    with TestClient(app) as client:
        response = client.get("/hallo3/pagination3/?limit=1001")
        assert response.status_code == 200

        response = client.get("/hallo3/pagination3/?offset=99")
        assert response.status_code == 200

        response = client.get("/hallo3/pagination3/?offset=99&limit=1001")
        assert response.status_code == 200


@override_settings(fastapi_app="tests.db.test_serializers.app")
def test_custom_pagination_invalid_offset_and_limit():

    class CustomPagination(Pagination):
        default_offset = 90
        default_limit = 1
        max_offset = 100
        max_limit = 2000

    @app.get("/hallo2/pagination2/")
    async def hallo2_pagination2(pagination: CustomPagination = Depends()):
        resp = await pagination.paginate(serializer_class=TestSerializer)
        return resp

    with TestClient(app) as client:
        response = client.get("/hallo2/pagination2/?limit=2001")
        assert response.status_code == 422

        response = client.get("/hallo2/pagination2/?offset=101")
        assert response.status_code == 422

        response = client.get("/hallo2/pagination2/?offset=101&limit=2001")
        assert response.status_code == 422


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_serializers.app")
async def test_paginate_equal_offset_limit():
    from fastapi_contrib.db.client import MongoDBClient

    MongoDBClient.__instance = None
    MongoDBClient._MongoDBClient__instance = None
    dumb_request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "query_string": b"limit=10&offset=10",
            "headers": {},
        }
    )
    pagination = Pagination(request=dumb_request, limit=10, offset=10)
    assert pagination.limit == 10
    assert pagination.offset == 10
    resp = await pagination.paginate(serializer_class=TestSerializer)
    assert resp == {
        "count": 1,
        "next": None,
        "previous": "/?limit=10",
        "result": [{"id": 1}],
    }


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_serializers.app")
async def test_paginate_offset_less_than_limit():
    from fastapi_contrib.db.client import MongoDBClient

    MongoDBClient.__instance = None
    MongoDBClient._MongoDBClient__instance = None
    dumb_request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "query_string": b"limit=10&offset=0",
            "headers": {},
        }
    )
    pagination = Pagination(request=dumb_request, limit=10, offset=0)
    assert pagination.limit == 10
    assert pagination.offset == 0
    resp = await pagination.paginate(serializer_class=TestSerializer)
    assert resp == {
        "count": 1,
        "next": None,
        "previous": None,
        "result": [{"id": 1}],
    }


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_serializers.app")
async def test_paginate_limit_less_than_offset():
    from fastapi_contrib.db.client import MongoDBClient

    MongoDBClient.__instance = None
    MongoDBClient._MongoDBClient__instance = None
    dumb_request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "query_string": b"limit=1&offset=10",
            "headers": {},
        }
    )
    pagination = Pagination(request=dumb_request, limit=1, offset=10)
    assert pagination.limit == 1
    assert pagination.offset == 10
    resp = await pagination.paginate(serializer_class=TestSerializer)
    assert resp == {
        "count": 1,
        "next": None,
        "previous": "/?limit=1&offset=9",
        "result": [{"id": 1}],
    }


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_serializers.app")
async def test_paginate_offset_less_than_zero():
    from fastapi_contrib.db.client import MongoDBClient

    MongoDBClient.__instance = None
    MongoDBClient._MongoDBClient__instance = None
    dumb_request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "query_string": b"limit=1&offset=-1",
            "headers": {},
        }
    )
    pagination = Pagination(request=dumb_request, limit=1, offset=-1)
    assert pagination.limit == 1
    assert pagination.offset == -1
    resp = await pagination.paginate(serializer_class=TestSerializer)
    assert resp == {
        "count": 1,
        "next": "/?limit=1&offset=0",
        "previous": None,
        "result": [{"id": 1}],
    }


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_serializers.app")
async def test_paginate_offset_with_additional_query_params():
    from fastapi_contrib.db.client import MongoDBClient

    MongoDBClient.__instance = None
    MongoDBClient._MongoDBClient__instance = None
    dumb_request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "query_string": b"additional=15&limit=0&offset=0",
            "headers": {},
        }
    )
    pagination = Pagination(request=dumb_request, limit=0, offset=0)
    assert pagination.limit == 0
    assert pagination.offset == 0
    resp = await pagination.paginate(serializer_class=TestSerializer)
    assert resp == {
        "count": 1,
        "next": "/?additional=15&limit=0&offset=0",
        "previous": None,
        "result": [{"id": 1}],
    }
