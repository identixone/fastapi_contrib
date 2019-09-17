from typing import Any, List

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request

from fastapi_contrib.common.responses import UJSONResponse


def parse_raw_error(err: Any) -> dict:
    """
    Parse single error object (such as pydantic-based or fastapi-based) to dict

    :param err: Error object
    :return: dict with name of the field (or "__all__") and actual message
    """
    if len(err.loc) == 2:
        name = err.loc[1]
    elif len(err.loc) == 1:
        name = err.loc[0]
    else:
        name = "__all__"
    return {"name": name, "message": err.msg.capitalize()}


def raw_errors_to_fields(raw_errors: List) -> List[dict]:
    """
    Translates list of raw errors (instances) into list of dicts with name/msg

    :param raw_errors: List with instances of raw error
    :return: List of dicts (1 dict for every raw error)
    """
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
    """
    Handles StarletteHTTPException, translating it into flat dict error data:
        * code - unique code of the error in the system
        * detail - general description of the error
        * fields - list of dicts with description of the error in each field

    :param request: Starlette Request instance
    :param exc: StarletteHTTPException instance
    :return: UJSONResponse with newly formatted error data
    """
    fields = getattr(exc, "fields", [])
    data = {
        "code": getattr(exc, "error_code", exc.status_code),
        "detail": getattr(exc, "message", exc.detail),
        "fields": fields,
    }
    return UJSONResponse(data, status_code=exc.status_code)


async def validation_exception_handler(
    request: Request, exc: ValidationError
) -> UJSONResponse:
    """
    Handles ValidationError, translating it into flat dict error data:
        * code - unique code of the error in the system
        * detail - general description of the error
        * fields - list of dicts with description of the error in each field

    :param request: Starlette Request instance
    :param exc: StarletteHTTPException instance
    :return: UJSONResponse with newly formatted error data
    """
    fields = raw_errors_to_fields(exc.raw_errors)
    status_code = getattr(exc, "status_code", 400)
    data = {
        "code": getattr(exc, "error_code", status_code),
        "detail": getattr(exc, "message", "Validation error"),
        "fields": fields,
    }
    return UJSONResponse(data, status_code=status_code)


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Helper function to setup exception handlers for app.
    Use during app startup as follows:

    .. code-block:: python

        app = FastAPI()

        @app.on_event('startup')
        async def startup():
            setup_exception_handlers(app)

    :param app: app object, instance of FastAPI
    :return: None
    """
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(
        RequestValidationError, validation_exception_handler
    )
    app.add_exception_handler(ValidationError, validation_exception_handler)
