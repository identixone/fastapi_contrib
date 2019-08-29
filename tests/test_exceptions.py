#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from fastapi_contrib.exceptions import (
    HTTPException, BadRequestError, ForbiddenError, NotFoundError)

from starlette import status


def test_http_exception():
    detail = "Random HTTP error happened."
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 999
    with pytest.raises(HTTPException) as excinfo:
        raise HTTPException(
            status_code=status_code, error_code=error_code,
            detail=detail
        )

    exc = excinfo.value
    assert exc.error_code == error_code
    assert exc.detail == detail
    assert exc.status_code == status_code


def test_bad_request_exception():
    detail = "Some really bad request was sent."
    error_code = 999
    with pytest.raises(BadRequestError) as excinfo:
        raise BadRequestError(
            error_code=error_code,
            detail=detail
        )

    exc = excinfo.value
    assert exc.error_code == error_code
    assert exc.detail == detail
    assert exc.status_code == status.HTTP_400_BAD_REQUEST


def test_forbidden_exception():
    detail = "You have no rights, peasant."
    with pytest.raises(ForbiddenError) as excinfo:
        raise ForbiddenError(
            detail=detail
        )

    exc = excinfo.value
    assert exc.error_code == status.HTTP_403_FORBIDDEN
    assert exc.status_code == status.HTTP_403_FORBIDDEN
    assert exc.detail == detail

    error_code = 444
    with pytest.raises(ForbiddenError) as excinfo:
        raise ForbiddenError(
            detail=detail,
            error_code=error_code
        )

    exc = excinfo.value
    assert exc.error_code == error_code
    assert exc.status_code == status.HTTP_403_FORBIDDEN
    assert exc.detail == detail


def test_not_found_exception():
    detail = "Nothing to see here."
    with pytest.raises(NotFoundError) as excinfo:
        raise NotFoundError(
            detail=detail
        )

    exc = excinfo.value
    assert exc.error_code == status.HTTP_404_NOT_FOUND
    assert exc.status_code == status.HTTP_404_NOT_FOUND
    assert exc.detail == detail

    error_code = 555
    with pytest.raises(NotFoundError) as excinfo:
        raise NotFoundError(
            detail=detail,
            error_code=error_code
        )

    exc = excinfo.value
    assert exc.error_code == error_code
    assert exc.status_code == status.HTTP_404_NOT_FOUND
    assert exc.detail == detail
