#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest.mock import patch

import pytest
import random

from datetime import datetime

import pytz
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorDatabase

from fastapi_contrib.auth.models import User, Token
from fastapi_contrib.db.utils import (
    default_id_generator,
    get_next_id,
    setup_mongodb,
    get_models,
    create_indexes,
)
from fastapi_contrib.common.utils import get_now
from tests.mock import MongoDBMock
from tests.utils import override_settings


app = FastAPI()
app.mongodb = MongoDBMock(
    collection_name="tokens", create_indexes_result="tokens")


def test_default_id_generator():
    _id = default_id_generator()
    assert _id.bit_length() <= 32


def test_get_now():
    _now = get_now()
    # import pdb;pdb.set_trace()
    assert datetime.now(tz=pytz.UTC) >= _now


def custom_get_now():
    return datetime.now()


@override_settings(now_function="tests.db.test_utils.custom_get_now")
def test_custom_get_now():
    _now = get_now()
    assert custom_get_now() >= _now


def custom_id_generator():
    bit_size = 32
    return random.getrandbits(bit_size)


@override_settings(
    mongodb_id_generator="tests.db.test_utils.custom_id_generator"
)
def test_get_next_id():
    _id = get_next_id()
    assert _id.bit_length() <= 32


def test_setup_mongodb():
    _app = FastAPI()
    setup_mongodb(_app)
    assert isinstance(_app.mongodb, AsyncIOMotorDatabase)


@override_settings(apps_folder_name="fastapi_contrib")
@override_settings(apps=["auth"])
def test_get_models():
    assert get_models() == [User, Token]


@override_settings(apps_folder_name="fastapi_contrib")
@override_settings(apps=["auth"])
@patch("pyclbr.readmodule")
def test_get_models_with_error_in_importing(mock_pyclbr):
    mock_pyclbr.side_effect = AttributeError()
    assert get_models() == []


@override_settings(apps_folder_name="apps")
@override_settings(apps=["auth"])
def test_get_models_not_found_apps_dir():
    # we don't have "apps" folder inside project root so models list is empty
    assert get_models() == []


@override_settings(apps_folder_name="fastapi_contrib")
@override_settings(apps=["common"])
def test_get_models_from_apps_without_models_module():
    assert get_models() == []


@override_settings(apps_folder_name="fastapi_contrib")
@override_settings(apps=[])
def test_get_models_from_empty_app_list():
    assert get_models() == []


@pytest.mark.asyncio
@override_settings(
    fastapi_app="tests.db.test_utils.app",
    apps_folder_name="fastapi_contrib",
    apps=["auth"]
)
async def test_create_indexes():
    created_indexes = await create_indexes()
    assert created_indexes == ["tokens"]
