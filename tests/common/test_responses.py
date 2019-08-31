#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi_contrib.common.responses import UJSONResponse


def test_ujson_response_helps_with_slashes():
    url = "http://hello.world/endpoint/?key=value"
    json = UJSONResponse().render(content={"url": url})
    assert json == f'{{"url":"{url}"}}'.encode('utf-8')
