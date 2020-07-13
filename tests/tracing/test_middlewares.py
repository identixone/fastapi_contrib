#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import MagicMock

import pytest

from fastapi import FastAPI
from jaeger_client import Tracer
from starlette.testclient import TestClient

from fastapi_contrib.tracing.middlewares import OpentracingMiddleware


def test_no_tracer_defined():
    app = FastAPI()
    app.add_middleware(OpentracingMiddleware)

    @app.get("/")
    async def index():
        ...

    with TestClient(app) as client:
        with pytest.raises(AttributeError):
            client.get("/")


def test_tracer_defined():
    app = FastAPI()
    mock_tracer = MagicMock(spec=Tracer)
    mock_tracer.return_value.__enter__.return_value = mock_tracer
    app.state.tracer = mock_tracer
    app.add_middleware(OpentracingMiddleware)

    @app.get("/")
    async def index():
        ...

    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
