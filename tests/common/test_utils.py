#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from asyncio import Future
from unittest.mock import MagicMock

from fastapi import FastAPI

from fastapi_contrib.common.utils import async_timing, resolve_dotted_path, \
    get_current_app
from tests.utils import override_settings


app = FastAPI()


def test_resolve_dotted_path():
    # TODO: more tests
    _Future = resolve_dotted_path("asyncio.Future")
    assert _Future == Future


@override_settings(fastapi_app="tests.common.test_utils.app")
def test_get_current_app():
    _app = get_current_app()
    assert _app == app


@pytest.mark.asyncio
async def test_async_timing_normal():
    func = MagicMock(return_value=Future())
    func.__name__ = 'func'
    func.return_value.set_result(None)
    decorated = async_timing(func)
    return_value = decorated()
    assert await return_value is None
    assert func.called


@pytest.mark.asyncio
@override_settings(debug_timing=True)
async def test_async_timing_without_debug_timing():
    func = MagicMock(return_value=Future())
    func.__name__ = 'func'
    func.return_value.set_result(None)
    decorated = async_timing(func)
    return_value = decorated()
    assert await return_value is None
    assert func.called


@pytest.mark.asyncio
async def test_async_timing_exception():
    func = MagicMock(return_value=Future())
    func.__name__ = 'func'
    func.return_value.set_result(None)
    func.side_effect = ValueError()
    decorated = async_timing(func)
    return_value = decorated()
    with pytest.raises(ValueError):
        assert await return_value is None
    assert func.call
