from typing import Any

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request

from fastapi_contrib.common.responses import UJSONResponse


def parse_raw_error(err: Any) -> dict:
    if len(err.loc) == 2:
        name = err.loc[1]
    elif len(err.loc) == 1:
        name = err.loc[0]
    else:
        name = "__all__"
    return {"name": name, "message": err.msg.capitalize()}


def raw_errors_to_fields(raw_errors: list) -> list:
    fields = []
    for top_err in raw_errors:
        if hasattr(top_err.exc, "raw_errors"):
            for err in top_err.exc.raw_errors:
                field_err = parse_raw_error(err)
                fields.append(field_err)
        else:
            field_err = parse_raw_error(top_err)
            fields.append(field_err)
    return fields


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> UJSONResponse:
    raw_errors = getattr(exc, "raw_errors", [])
    data = {
        "code": getattr(exc, "error_code", exc.status_code),
        "detail": getattr(exc, "message", exc.detail),
        "fields": raw_errors_to_fields(raw_errors),
    }
    return UJSONResponse(data, status_code=exc.status_code)


async def validation_exception_handler(
    request: Request, exc: ValidationError
) -> UJSONResponse:
    fields = raw_errors_to_fields(exc.raw_errors)
    status_code = getattr(exc, "status_code", 400)
    data = {
        "code": getattr(exc, "error_code", status_code),
        "detail": getattr(exc, "message", "Validation error"),
        "fields": fields,
    }
    return UJSONResponse(data, status_code=status_code)


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(
        RequestValidationError, validation_exception_handler
    )
    app.add_exception_handler(ValidationError, validation_exception_handler)
