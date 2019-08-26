import importlib
import motor.motor_asyncio
import pkgutil
import pyclbr
import os
import uuid

from datetime import datetime

from fastapi_contrib.common.utils import resolve_dotted_path
from fastapi_contrib.conf import settings


def default_id_generator():
    """
    :return: 64-bit int ID
    """
    bit_size = 64
    return uuid.uuid4().int >> bit_size


def get_now():
    if settings.now_function:
        return resolve_dotted_path(settings.now_function)()
    return datetime.utcnow()


def get_next_id():
    id_generator = resolve_dotted_path(settings.mongodb_id_generator)
    return id_generator()


def setup_mongodb(app):
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_dsn)
    app.mongodb = client[settings.mongodb_dbname]


def get_db_client():
    from fastapi_contrib.db.client import MongoDBClient
    client = MongoDBClient()
    return client


def get_models():
    from fastapi_contrib.db.models import MongoDBModel

    path = os.path.dirname(settings.project_root)
    models = []
    for app in settings.apps:
        modules = [f[1] for f in pkgutil.walk_packages(path=[f"{path}/{app}"])]
        if "models" in modules:
            module_models = pyclbr.readmodule(f"apps.{app}.models").keys()
            mudule = importlib.import_module(f"apps.{app}.models")
            models.extend([getattr(mudule, model) for model in module_models])

    return list(filter(lambda x: issubclass(x, MongoDBModel), models))


async def create_indexes():
    models = get_models()
    for model in models:
        await model.create_indexes()
