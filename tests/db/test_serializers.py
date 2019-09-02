#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from pydantic import BaseModel, ValidationError

from fastapi_contrib.db.serializers import Serializer, ModelSerializer


def test_serializer_inheritance_works():
    class TestSerializer(Serializer):
        a = 1

        def b(self):
            return "b"

    serializer = TestSerializer()
    assert serializer.a == 1
    assert serializer.b() == "b"


def test_model_serializer_inheritance_works():
    class Model(BaseModel):
        ...

    class TestSerializer(ModelSerializer):
        a = 1
        c: str
        d: int = None

        def b(self):
            return "b"

        class Meta:
            model = Model

    serializer = TestSerializer(c="2", d=3)
    assert serializer.a == 1
    assert serializer.c == "2"
    assert serializer.d == 3
    assert serializer.b() == "b"

    with pytest.raises(ValidationError):
        TestSerializer(c=dict(), d="asd")

    with pytest.raises(ValidationError):
        TestSerializer(c=None, d=None)

    with pytest.raises(ValidationError):
        TestSerializer()
