from typing import Any, List, Optional

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request

from fastapi_contrib.common.responses import UJSONResponse


def parse_error(
    err: Any, field_names: List, raw: bool = True
) -> Optional[dict]:
    """
    Parse single error object (such as pydantic-based or fastapi-based) to dict

    :param err: Error object
    :param field_names: List of names of the field that are already processed
    :param raw: Whether this is a raw error or wrapped pydantic error
    :return: dict with name of the field (or "__all__") and actual message
    """
    if err.type_ == "value_error.str.regex":
        message = "Provided value doesn't match valid format."
    elif err.type_ == "type_error.enum":
        message = "One or more values provided are not valid."
    else:
        message = err.msg or ""
    if not raw:
        if len(err.loc) == 2:
            if str(err.loc[0]) == "body":
                name = err.loc[1]
            else:
                name = err.loc[0]
        elif len(err.loc) == 1:
            if str(err.loc[0]) == "body":
                name = "__all__"
            else:
                name = str(err.loc[0])
        else:
            name = "__all__"
    else:
        if len(err.loc) == 2:
            name = str(err.loc[0])
            message = f"{str(err.loc[1]).lower()}: {message}"
        elif len(err.loc) == 1:
            name = str(err.loc[0])
        else:
            name = "__all__"

    if name in field_names:
        return None

    return {"name": name, "message": message.capitalize()}


def raw_errors_to_fields(raw_errors: List) -> List[dict]:
    """
    Translates list of raw errors (instances) into list of dicts with name/msg

    :param raw_errors: List with instances of raw error
    :return: List of dicts (1 dict for every raw error)
    """
    # import pdb;pdb.set_trace()
    fields = []
    for top_err in raw_errors:
        if hasattr(top_err.exc, "raw_errors"):
            for err in top_err.exc.raw_errors:
                field_err = parse_error(
                    err,
                    field_names=list(map(lambda x: x["name"], fields)),
                    raw=True
                )
                if field_err is not None:
                    fields.append(field_err)
        else:
            field_err = parse_error(
                top_err,
                field_names=list(map(lambda x: x["name"], fields)),
                raw=False
            )
            if field_err is not None:
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
    request: Request, exc: RequestValidationError
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


async def internal_server_error_handler(
    request: Request, exc: RequestValidationError
) -> UJSONResponse:
    code = exc.error_code if hasattr(exc, "error_code") else 500
    detail = exc.detail if hasattr(exc, "detail") else "Internal Server Error."
    fields = exc.fields if hasattr(exc, "fields") else []
    status_code = exc.status_code if hasattr(exc, "status_code") else 500
    data = {"code": code, "detail": detail, "fields": fields}
    return UJSONResponse(data, status_code=status_code)


async def not_found_error_handler(
    request: Request, exc: RequestValidationError
) -> UJSONResponse:
    code = exc.error_code if hasattr(exc, "error_code") else 404
    detail = exc.detail if hasattr(exc, "detail") else "Not found."
    fields = exc.fields if hasattr(exc, "fields") else []
    status_code = exc.status_code if hasattr(exc, "status_code") else 404
    data = {"code": code, "detail": detail, "fields": fields}
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
    app.add_exception_handler(404, not_found_error_handler)
    app.add_exception_handler(500, internal_server_error_handler)
