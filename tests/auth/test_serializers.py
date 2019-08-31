#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi_contrib.auth.models import Token
from fastapi_contrib.auth.serializers import TokenSerializer


def test_token_serializer():
    serializer = TokenSerializer()
    assert serializer.Meta.model == Token
    assert "user_id" not in serializer.dict().keys()
