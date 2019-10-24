from fastapi import FastAPI
from jaeger_client import Tracer

from fastapi_contrib.tracing.utils import setup_opentracing


def test_setup_opentracing():
    _app = FastAPI()
    setup_opentracing(_app)
    assert isinstance(_app.tracer, Tracer)
