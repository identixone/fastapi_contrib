#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from fastapi import FastAPI

from pydantic import BaseModel, ValidationError

from fastapi_contrib.db.models import MongoDBTimeStampedModel
from fastapi_contrib.serializers import openapi
from fastapi_contrib.serializers.common import Serializer, ModelSerializer
from tests.mock import MongoDBMock
from tests.utils import override_settings

app = FastAPI()
app.mongodb = MongoDBMock()


def test_serializer_inheritance_works():
    @openapi.patch
    class TestSerializer(Serializer):
        a = 1

        def b(self):
            return "b"

    serializer = TestSerializer()
    assert serializer.a == 1
    assert serializer.b() == "b"


def test_model_serializer_inheritance_works():
    class Model(BaseModel):
        e: int = 2
        f: str

    @openapi.patch
    class TestSerializer(ModelSerializer):
        a = 1
        c: str
        d: int = None

        def b(self):
            return "b"

        class Meta:
            model = Model

    serializer = TestSerializer(c="2", d=3, f="4")
    assert serializer.a == 1
    assert serializer.c == "2"
    assert serializer.d == 3
    assert serializer.b() == "b"
    assert serializer.e == 2
    assert serializer.f == "4"

    with pytest.raises(ValidationError):
        TestSerializer(c=dict(), d="asd")

    with pytest.raises(ValidationError):
        TestSerializer(c=None, d=None)

    with pytest.raises(ValidationError):
        TestSerializer()


def test_sanitize_list_serializer():
    @openapi.patch
    class TestSerializer(Serializer):
        a: int = 1

    data = [{"a": 1}, {"b": 2}, {"c": 3}]
    sanitized_data = TestSerializer.sanitize_list(data)
    assert data == sanitized_data

    @openapi.patch
    class TestSerializer(Serializer):
        a: int = 1

        class Meta:
            exclude: set = {"b", "c"}

    data = [{"a": 1, "b": 2}, {"b": 2}, {"c": 3}]
    sanitized_data = TestSerializer.sanitize_list(data)
    assert [{"a": 1}, {}, {}] == sanitized_data


@pytest.mark.asyncio
async def test_serializer_save():
    @openapi.patch
    class TestSerializer(Serializer):
        a: int = 1

    serializer = TestSerializer()
    await serializer.save()
    assert not hasattr(serializer, "id")


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_serializers.app")
async def test_model_serializer_save():
    class Model(MongoDBTimeStampedModel):

        class Meta:
            collection = "collection"

    @openapi.patch
    class TestSerializer(ModelSerializer):
        a = 1
        c: str
        d: int = None

        class Meta:
            model = Model

    serializer = TestSerializer(c="2")
    instance = await serializer.save()
    assert instance.id == 1


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_serializers.app")
async def test_model_serializer_update_one():
    class Model(MongoDBTimeStampedModel):

        class Meta:
            collection = "collection"

    @openapi.patch
    class TestSerializer(ModelSerializer):
        a = 1
        c: str
        d: int = None

        class Meta:
            model = Model

    serializer = TestSerializer(c="2")
    result = await serializer.update_one({"a": 1})
    assert result.raw_result == {}


@pytest.mark.asyncio
@override_settings(fastapi_app="tests.db.test_serializers.app")
async def test_model_serializer_update_many():
    class Model(MongoDBTimeStampedModel):

        class Meta:
            collection = "collection"

    @openapi.patch
    class TestSerializer(ModelSerializer):
        a = 1
        c: str
        d: int = None

        class Meta:
            model = Model

    serializer = TestSerializer(c="2")
    result = await serializer.update_many({"a": 1})
    assert result.raw_result == {}


def test_serializer_dict():
    @openapi.patch
    class TestSerializer(Serializer):
        a: int = 1

    serializer = TestSerializer()
    _dict = serializer.dict()
    assert _dict == {"a": 1}

    @openapi.patch
    class TestSerializer(Serializer):
        a: int = 1
        b: str

        class Meta:
            exclude: set = {"a"}

    serializer = TestSerializer(b="b")
    _dict = serializer.dict()
    assert _dict == {"b": "b"}

    _dict = serializer.dict(exclude={"b"})
    assert _dict == {}


def test_model_serializer_dict():
    @openapi.patch
    class TestSerializer(ModelSerializer):
        a = 1
        c: str
        d: int = None

        class Meta:
            write_only_fields: set = {"c"}
            exclude: set = {"d"}

    serializer = TestSerializer(c="2")
    _dict = serializer.dict()
    assert _dict == {"a": 1}
