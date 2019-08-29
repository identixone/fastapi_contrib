#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

os.environ["CONTRIB_FASTAPI_APP"] = "app"
os.environ["CONTRIB_PROJECT_ROOT"] = "."

from fastapi_contrib.conf import settings


def test_settings_from_env_and_defaults():
    assert settings.fastapi_app == "app"
    assert settings.project_root == "."
    assert settings.now_function is None
