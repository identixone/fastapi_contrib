from typing import Any, List, Optional

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import EnumError, StrRegexError
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

    if isinstance(err.exc, EnumError):
        permitted_values = ", ".join(
            [f"'{val}'" for val in err.exc.enum_values]
        )
        message = f"Value is not a valid enumeration member; " \
                  f"permitted: {permitted_values}."
    elif isinstance(err.exc, StrRegexError):
        message = "Provided value doesn't match valid format."
    else:
        message = str(err.exc) or ""

    if hasattr(err.exc, "code") and err.exc.code.startswith("error_code"):
        error_code = int(err.exc.code.split(".")[-1])
    else:
        # default error code for non-custom errors is 400
        error_code = 400

    if not raw:
        if len(err.loc_tuple()) == 2:
            if str(err.loc_tuple()[0]) in ["body", "query"]:
                name = err.loc_tuple()[1]
            else:
                name = err.loc_tuple()[0]
        elif len(err.loc_tuple()) == 1:
            if str(err.loc_tuple()[0]) == "body":
                name = "__all__"
            else:
                name = str(err.loc_tuple()[0])
        else:
            name = "__all__"
    else:
        if len(err.loc_tuple()) == 2:
            name = str(err.loc_tuple()[0])
        elif len(err.loc_tuple()) == 1:
            name = str(err.loc_tuple()[0])
        else:
            name = "__all__"

    if name in field_names:
        return None

    if message and not any(
        [message.endswith("."), message.endswith("?"), message.endswith("!")]
    ):
        message = message + "."
    message = message.capitalize()

    return {"name": name, "message": message, "error_code": error_code}


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
                # This is a special case when errors happen both in request
                # handling & internal validation
                if isinstance(err, list):
                    err = err[0]
                field_err = parse_error(
                    err,
                    field_names=list(map(lambda x: x["name"], fields)),
                    raw=True,
                )
                if field_err is not None:
                    fields.append(field_err)
        else:
            field_err = parse_error(
                top_err,
                field_names=list(map(lambda x: x["name"], fields)),
                raw=False,
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
    message = getattr(exc, "detail", "Validation error.")
    headers = getattr(exc, "headers", None)
    if message and not any(
        [message.endswith("."), message.endswith("?"), message.endswith("!")]
    ):
        message = message + "."
    data = {
        "error_codes": [getattr(exc, "error_code", exc.status_code)],
        "message": message,
        "fields": fields,
    }
    return UJSONResponse(data, status_code=exc.status_code, headers=headers)


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
    status_code = getattr(exc, "status_code", 400)
    headers = getattr(exc, "headers", None)
    fields = raw_errors_to_fields(exc.raw_errors)

    if fields:
        error_codes = set(list(map(lambda x: x["error_code"], fields)))
    else:
        error_codes = [getattr(exc, "error_code", status_code)]

    message = getattr(exc, "message", "Validation error.")
    if message and not any(
        [message.endswith("."), message.endswith("?"), message.endswith("!")]
    ):
        message = message + "."  # pragma: no cover

    data = {"error_codes": error_codes, "message": message, "fields": fields}
    return UJSONResponse(data, status_code=status_code, headers=headers)


async def not_found_error_handler(
    request: Request, exc: RequestValidationError
) -> UJSONResponse:
    code = getattr(exc, "error_code", 404)
    detail = getattr(exc, "detail", "Not found.")
    fields = getattr(exc, "fields", [])
    headers = getattr(exc, "headers", None)
    status_code = getattr(exc, "status_code", 404)
    data = {"error_codes": [code], "message": detail, "fields": fields}
    return UJSONResponse(data, status_code=status_code, headers=headers)


async def internal_server_error_handler(
    request: Request, exc: RequestValidationError
) -> UJSONResponse:
    code = getattr(exc, "error_code", 500)
    detail = getattr(exc, "detail", "Internal Server Error.")
    fields = getattr(exc, "fields", [])
    headers = getattr(exc, "headers", None)
    status_code = getattr(exc, "status_code", 500)
    data = {"error_codes": [code], "message": detail, "fields": fields}
    return UJSONResponse(data, status_code=status_code, headers=headers)


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
