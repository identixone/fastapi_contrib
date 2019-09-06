import importlib
import motor.motor_asyncio
import pkgutil
import pyclbr
import random

from datetime import datetime
from typing import List

from fastapi_contrib.common.utils import resolve_dotted_path
from fastapi_contrib.conf import settings


def default_id_generator():
    """
    TODO: there were some problems with 64-bit ints, needs investigation
    :return: 32-bit int ID
    """
    bit_size = 32
    return random.getrandbits(bit_size)


def get_now():
    # TODO: cache this
    if settings.now_function:
        return resolve_dotted_path(settings.now_function)()
    return datetime.utcnow()


def get_next_id():
    # TODO: cache this
    id_generator = resolve_dotted_path(settings.mongodb_id_generator)
    return id_generator()


def setup_mongodb(app):
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_dsn)
    app.mongodb = client[settings.mongodb_dbname]


def get_db_client():
    from fastapi_contrib.db.client import MongoDBClient
    client = MongoDBClient()
    return client


def get_models() -> list:
    from fastapi_contrib.db.models import MongoDBModel
    apps_folder_name = settings.apps_folder_name
    path = settings.project_root
    models = []
    for app in settings.apps:
        modules = [f[1] for f in pkgutil.walk_packages(path=[f"{path}/{app}"])]
        if "models" in modules:
            try:
                module_models = pyclbr.readmodule(f"{apps_folder_name}.{app}.models").keys()
            except AttributeError:
                # TODO: print warning or something
                continue
            mudule = importlib.import_module(f"{apps_folder_name}.{app}.models")
            models.extend([getattr(mudule, model) for model in module_models])

    return list(filter(lambda x: issubclass(x, MongoDBModel), models))


async def create_indexes() -> List[str]:
    models = get_models()
    indexes = []
    for model in models:
        indexes.append(await model.create_indexes())
    return list(filter(None, indexes))
