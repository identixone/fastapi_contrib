#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from fastapi import FastAPI

from fastapi_contrib.db.client import MongoDBClient
from fastapi_contrib.db.models import MongoDBModel
from tests.mock import MongoDBMock
from tests.utils import override_settings

app = FastAPI()
app.mongodb = MongoDBMock()


class Model(MongoDBModel):
    class Meta:
        collection = "collection"


@override_settings(fastapi_app="tests.db.test_client.app")
def test_mongodbclient_is_singleton():
    client = MongoDBClient()
    assert client == MongoDBClient()


@override_settings(fastapi_app="tests.db.test_client.app")
def test_get_collection():
    client = MongoDBClient()
    collection = client.get_collection("collection")
    assert collection.name == "collection"


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_client.app")
async def test_insert():
    client = MongoDBClient()
    model = Model(id=1)
    insert_result = await client.insert(model)
    assert insert_result.inserted_id == model.id


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_client.app")
async def test_count():
    client = MongoDBClient()
    model = Model(id=1)
    count = await client.count(model, id=1)
    assert count == 1

    # Test whether it correctly handles filter by non-id
    count = await client.count(model, field="value")
    assert count == 1


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_client.app")
async def test_delete():
    client = MongoDBClient()
    model = Model(id=1)
    delete_result = await client.delete(model, id=1)
    assert delete_result.raw_result == {}

    # Test whether it correctly handles filter by non-id
    delete_result = await client.delete(model, field="value")
    assert delete_result.raw_result == {}


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_client.app")
async def test_update_one():
    client = MongoDBClient()
    model = Model(id=1)
    update_result = await client.update_one(
        model, filter_kwargs={"id": 1}, id=2
    )
    assert update_result.raw_result == {}

    # Test whether it correctly handles filter by non-id
    update_result = await client.update_one(
        model, filter_kwargs={"field": "value"}, field="value2"
    )
    assert update_result.raw_result == {}


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_client.app")
async def test_get():
    client = MongoDBClient()
    model = Model(id=1)
    _dict = await client.get(model, id=1)
    assert _dict == {"_id": 1}

    # Test whether it correctly handles filter by non-id
    _dict = await client.get(model, field="value")
    assert _dict == {"_id": 1}


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_client.app")
async def test_list():
    client = MongoDBClient()
    model = Model(id=1)
    cursor = client.list(model, id=1)
    assert cursor

    # Test whether it correctly handles filter by non-id
    _dict = client.list(model, field="value")
    assert cursor
