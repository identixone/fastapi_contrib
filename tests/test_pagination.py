#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from fastapi import FastAPI
from starlette.requests import Request

from fastapi_contrib.db.models import MongoDBTimeStampedModel
from fastapi_contrib.db.serializers import ModelSerializer
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


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_serializers.app")
async def test_paginate_no_filters():
    from fastapi_contrib.db.client import MongoDBClient

    MongoDBClient.__instance = None
    MongoDBClient._MongoDBClient__instance = None
    dumb_request = Request({"type": "http", "method": "GET", "path": "/"})
    pagination = Pagination(request=dumb_request)
    resp = await pagination.paginate(serializer_class=TestSerializer)
    assert resp == {
        "count": 1,
        "next": None,
        "previous": None,
        "result": [{"id": 1}],
    }


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_serializers.app")
async def test_paginate_zero_offset_zero_limit():
    from fastapi_contrib.db.client import MongoDBClient

    MongoDBClient.__instance = None
    MongoDBClient._MongoDBClient__instance = None
    dumb_request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "query_string": b"?limit=0&offset=0",
            "headers": {},
        }
    )
    pagination = Pagination(request=dumb_request, limit=0, offset=0)
    assert pagination.limit == 0
    assert pagination.offset == 0
    resp = await pagination.paginate(serializer_class=TestSerializer)
    assert resp == {
        "count": 1,
        "next": "/?limit=0&offset=0",
        "previous": None,
        "result": [{"id": 1}],
    }


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
            "query_string": b"?limit=10&offset=10",
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
        "previous": "/?%3Flimit=10",
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
            "query_string": b"?limit=10&offset=0",
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
            "query_string": b"?limit=1&offset=10",
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
            "query_string": b"?limit=1&offset=-1",
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
