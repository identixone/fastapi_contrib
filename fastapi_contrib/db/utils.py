import importlib
import motor.motor_asyncio
import pkgutil
import pyclbr
import random

from datetime import datetime
from typing import List

from fastapi import FastAPI

from fastapi_contrib.common.utils import resolve_dotted_path
from fastapi_contrib.conf import settings


def default_id_generator(bit_size: int = 32) -> int:
    """
    Generator of IDs for newly created MongoDB rows.

    :return: `bit_size` long int
    """
    return random.getrandbits(bit_size)


def get_now() -> datetime:
    """
    Retrieves `now` function from the path, specified in project's conf.
    :return: datetime of "now"
    """
    # TODO: cache this
    if settings.now_function:
        return resolve_dotted_path(settings.now_function)()
    return datetime.utcnow()


def get_next_id() -> int:
    """
    Retrieves ID generator function from the path, specified in project's conf.
    :return: newly generated ID
    """
    # TODO: cache this
    id_generator = resolve_dotted_path(settings.mongodb_id_generator)
    return id_generator()


def setup_mongodb(app: FastAPI) -> None:
    """
    Helper function to setup MongoDB connection & `motor` client during setup.
    Use during app startup as follows:

    .. code-block:: python

        app = FastAPI()

        @app.on_event('startup')
        async def startup():
            setup_mongodb(app)

    :param app: app object, instance of FastAPI
    :return: None
    """
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_dsn)
    app.mongodb = client[settings.mongodb_dbname]


def get_db_client():
    """
    Gets instance of MongoDB client for you to make DB queries.
    :return: MongoDBClient
    """
    from fastapi_contrib.db.client import MongoDBClient

    client = MongoDBClient()
    return client


def get_models() -> list:
    """
    Scans `settings.apps_folder_name`, relative to `settings.project_root`.
    Find `models` module in each of them and searches for any attributes there.
    Last step is to filter attributes to return only those,
    subclassed from MongoDBModel (or timestamped version).

    Used internally only by `create_indexes` function.

    :return: list of user-defined models (subclassed from MongoDBModel) in apps
    """
    from fastapi_contrib.db.models import MongoDBModel

    apps_folder_name = settings.apps_folder_name
    path = settings.project_root
    models = []
    for app in settings.apps:
        modules = [f[1] for f in pkgutil.walk_packages(path=[f"{path}/{app}"])]
        if "models" in modules:
            try:
                module_models = pyclbr.readmodule(
                    f"{apps_folder_name}.{app}.models"
                ).keys()
            except AttributeError:
                # TODO: print warning or something
                continue
            mudule = importlib.import_module(
                f"{apps_folder_name}.{app}.models"
            )
            models.extend([getattr(mudule, model) for model in module_models])

    return list(filter(lambda x: issubclass(x, MongoDBModel), models))


async def create_indexes() -> List[str]:
    """
    Gets all models in project and then creates indexes for each one of them.
    :return: list of indexes that has been invoked to create
             (could've been created earlier, it doesn't raise in this case)
    """
    models = get_models()
    indexes = []
    for model in models:
        indexes.append(await model.create_indexes())
    return list(filter(None, indexes))
