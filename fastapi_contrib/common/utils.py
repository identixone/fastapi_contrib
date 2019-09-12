import importlib
import sys

from functools import wraps
from time import time

from fastapi_contrib.conf import settings


def resolve_dotted_path(path: str):
    splitted = path.split(".")
    if len(splitted) <= 1:
        return importlib.import_module(path)
    module, attr = ".".join(splitted[:-1]), splitted[-1]
    module = importlib.import_module(module)
    return getattr(module, attr)


def get_logger():
    logger = resolve_dotted_path(settings.logger)

    # Check whether it is loguru-compatible logger
    if hasattr(logger, "configure"):
        logger_config = {
            "handlers": [
                {
                    "sink": sys.stdout,
                    "level": settings.log_level,
                    "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                    "<level>{level: <8}</level> | "
                    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:"
                    "<cyan>{line}</cyan> -"
                    " <level>{message}</level>",
                }
            ]
        }
        logger.configure(**logger_config)

    return logger


logger = get_logger()


def get_current_app():
    # TODO: cache this
    app = resolve_dotted_path(settings.fastapi_app)
    return app


def async_timing(func):
    @wraps(func)
    async def wrap(*args, **kwargs):
        time1 = time()

        raised_exception = True
        try:
            ret = await func(*args, **kwargs)
            raised_exception = False
            if not settings.debug_timing:
                return ret
        finally:
            time2 = time()
            duration = (time2 - time1) * 1000.0

            logger.debug(
                "\t [TIMING] {:s} {:s} {:.3f} ms".format(
                    func.__module__.ljust(20),
                    func.__name__.ljust(20),
                    duration,
                )
            )

            if not raised_exception:
                return ret

    return wrap
