from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse


def parse_exc_dict(exc_dict):
    if not isinstance(exc_dict, dict):
        exc_dict = {"__all__": exc_dict}

    for k, v in exc_dict.items():
        exc_dict = {"field": k, "message": v}
        break

    return exc_dict


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
):
    errors = []

    if isinstance(exc.detail, list):
        for exc_dict in exc.detail:
            errors.append(parse_exc_dict(exc_dict))
    else:
        errors.append(parse_exc_dict(exc.detail))

    message = getattr(exc, "message", "Bad Request")
    data = {"errors": errors, "message": message}

    if hasattr(exc, "error_code"):
        data.update({"code": exc.error_code})
    return JSONResponse(data, status_code=exc.status_code)


async def fastapi_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    errors = {}
    for err in exc.raw_errors:
        for raw_err in err.exc.args:
            errors.update({raw_err[0].loc[0]: raw_err[0].msg})

    data = {"message": "Validation Failed", "code": 400, "errors": errors}
    return JSONResponse(data, status_code=400)


async def validation_exception_handler(request: Request, exc: ValidationError):
    errors = {}
    for err in exc.raw_errors:
        if isinstance(err, list) or isinstance(err, tuple):
            for raw_err in err.exc.args:
                errors.update({err.loc[0]: raw_err})
        else:
            errors.update({err.loc[0]: err.msg})

    data = {"message": "Validation Failed", "code": 400, "errors": errors}
    return JSONResponse(data, status_code=400)


def setup_exception_handlers(app):
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(
        RequestValidationError, fastapi_validation_exception_handler
    )
    app.add_exception_handler(ValidationError, validation_exception_handler)
