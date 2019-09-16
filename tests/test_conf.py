#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi_contrib.conf import settings


def test_settings_from_env_and_defaults():
    assert settings.fastapi_app == "tests.conftest.app"
    assert settings.now_function is None
