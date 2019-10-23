#!/usr/bin/env python
# -*- coding: utf-8 -*-
from asyncio import Future

import pytest

from fastapi import FastAPI

from fastapi_contrib.db.client import MongoDBClient
from fastapi_contrib.db.models import MongoDBModel, MongoDBTimeStampedModel
from tests.mock import MongoDBMock
from tests.utils import override_settings, AsyncMock, AsyncIterator
from unittest.mock import patch

app = FastAPI()
app.mongodb = MongoDBMock()


class Model(MongoDBModel):
    class Meta:
        collection = "collection"


@override_settings(fastapi_app="tests.db.test_client.app")
def test_mongodbclient_is_singleton():
    MongoDBClient.__instance = None
    MongoDBClient._MongoDBClient__instance = None

    client = MongoDBClient()
    assert client == MongoDBClient()


@override_settings(fastapi_app="tests.db.test_client.app")
def test_get_collection():
    MongoDBClient.__instance = None
    MongoDBClient._MongoDBClient__instance = None

    client = MongoDBClient()
    collection = client.get_collection("collection")
    assert collection.name == "collection"


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_client.app")
async def test_insert():
    MongoDBClient.__instance = None
    MongoDBClient._MongoDBClient__instance = None

    client = MongoDBClient()
    model = Model(id=1)
    insert_result = await client.insert(model)
    assert insert_result.inserted_id == model.id


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_client.app")
async def test_count():
    MongoDBClient.__instance = None
    MongoDBClient._MongoDBClient__instance = None

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
    MongoDBClient.__instance = None
    MongoDBClient._MongoDBClient__instance = None

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
    MongoDBClient.__instance = None
    MongoDBClient._MongoDBClient__instance = None

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
async def test_update_one_params():
    with patch('fastapi_contrib.db.client.MongoDBClient.update_one', new_callable=AsyncMock) as mock_update:
        class Model(MongoDBTimeStampedModel):

            class Meta:
                collection = "collection"

        client = MongoDBClient()

        model = Model()

        await model.update_one(
            filter_kwargs={"id": 1}, kwargs={'$set': {'bla': 1}}
        )

        mock_update.mock.assert_called_with(client, Model, filter_kwargs={'id': 1}, kwargs={'$set': {'bla': 1}})


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_client.app")
async def test_update_many_params():
    with patch('fastapi_contrib.db.client.MongoDBClient.update_many', new_callable=AsyncMock) as mock_update:
        class Model(MongoDBTimeStampedModel):
            class Meta:
                collection = "collection"

        client = MongoDBClient()

        model = Model()

        await model.update_many(
            filter_kwargs={"id": 1}, kwargs={'$set': {'bla': 1}}
        )

        mock_update.mock.assert_called_with(client, Model, filter_kwargs={'id': 1}, kwargs={'$set': {'bla': 1}})


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_client.app")
async def test_update_many():
    MongoDBClient.__instance = None
    MongoDBClient._MongoDBClient__instance = None

    client = MongoDBClient()
    model = Model(id=1)
    update_result = await client.update_many(
        model, filter_kwargs={"id": 1}, id=2
    )
    assert update_result.raw_result == {}

    # Test whether it correctly handles filter by non-id
    update_result = await client.update_many(
        model, filter_kwargs={"field": "value"}, field="value2"
    )
    assert update_result.raw_result == {}


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_client.app")
async def test_get():
    MongoDBClient.__instance = None
    MongoDBClient._MongoDBClient__instance = None

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
    MongoDBClient.__instance = None
    MongoDBClient._MongoDBClient__instance = None

    client = MongoDBClient()
    model = Model(id=1)
    cursor = client.list(model, id=1)
    assert cursor

    # Test whether it correctly handles filter by non-id
    _dict = client.list(model, field="value")
    assert _dict


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_client.app")
async def test_list_with_sort():
    with patch('fastapi_contrib.db.client.MongoDBClient.list') as mock_update:

        mock_update.return_value = AsyncIterator([])

        class Model(MongoDBTimeStampedModel):

            class Meta:
                collection = "collection"

        model = Model()

        await model.list(model, _limit=0, _offset=0, _sort=[('i', -1)])

        mock_update.assert_called_with(Model, _limit=0, _offset=0, _sort=[('i', -1)])

        await model.list(model)

        mock_update.assert_called_with(Model, _limit=0, _offset=0, _sort=None)
