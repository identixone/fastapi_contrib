#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from datetime import datetime
from fastapi import FastAPI

from fastapi_contrib.db.models import MongoDBTimeStampedModel
from tests.mock import MongoDBMock
from tests.utils import override_settings

app = FastAPI()
app.mongodb = MongoDBMock()


class Model(MongoDBTimeStampedModel):
    class Meta:
        collection = "collection"


def test_set_id():
    instance = Model()
    assert instance.id is not None

    instance = Model(id=321)
    assert instance.id == 321


def test_set_created():
    instance = Model()
    assert instance.created is not None
    assert isinstance(instance.created, datetime)
    instance = Model(created=datetime.utcnow())
    assert instance.created <= datetime.utcnow()


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_models.app")
async def test_get():
    instance = await Model.get(id=1)
    assert instance.id == 1


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_models.app")
async def test_get_not_found():
    app.mongodb = MongoDBMock(find_one_result=None)
    instance = await Model.get(id=1)
    assert instance is None


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_models.app")
async def test_delete():
    result = await Model.delete(id=1)
    assert result.raw_result == {}


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_models.app")
async def test_count():
    result = await Model.count(id=1)
    assert result == 1


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_models.app")
async def test_list():
    _list = await Model.list(id=1)
    assert _list == [{"id": 1}]


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_models.app")
async def test_list_raw():
    iterator = await Model.list(raw=False, id=1)
    _list = list(iterator)
    assert isinstance(_list[0], Model)
    assert _list[0].id == 1
    assert not hasattr(list(_list)[0], "_id")


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_models.app")
async def test_update_one():
    result = await Model.update_one(filter_kwargs={"id": 1}, id=2)
    assert result.raw_result == {}


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_models.app")
async def test_update_many():
    result = await Model.update_many(filter_kwargs={"id": 1}, id=2)
    assert result.raw_result == {}
