#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi_contrib.auth.models import Token


def test_token_without_key_generation():
    t = Token(key="hello")
    assert t.key == "hello"


def test_tokenkey_generation():
    t = Token()
    assert t.key is not None and t.key != ""
