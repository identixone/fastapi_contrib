import importlib
import motor.motor_asyncio
import pkgutil
import pyclbr
import random
import inspect

from typing import List

from fastapi import FastAPI

from fastapi_contrib.common.utils import logger, resolve_dotted_path
from fastapi_contrib.conf import settings


def default_id_generator(bit_size: int = 32) -> int:
    """
    Generator of IDs for newly created MongoDB rows.

    :return: `bit_size` long int
    """
    return random.getrandbits(bit_size)


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
    client = motor.motor_asyncio.AsyncIOMotorClient(
        settings.mongodb_dsn,
        minPoolSize=settings.mongodb_min_pool_size,
        maxPoolSize=settings.mongodb_max_pool_size,
    )
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
    Scans `settings.apps_folder_name`.
    Find `models` modules in each of them and get all attributes there.
    Last step is to filter attributes to return only those,
    subclassed from MongoDBModel (or timestamped version).

    Used internally only by `create_indexes` function.

    :return: list of user-defined models (subclassed from MongoDBModel) in apps
    """
    from fastapi_contrib.db.models import MongoDBModel

    apps_folder_name = settings.apps_folder_name
    models = []
    for app in settings.apps:
        app_path = f"{apps_folder_name}/{app}"
        modules = [
            f for f in pkgutil.walk_packages(path=[app_path])
            if f.name == 'models'
        ]
        if not modules:
            continue
        for module in modules:
            path_to_models = f"{apps_folder_name}.{app}.models"
            mudule = importlib.import_module(path_to_models)
            if module.ispkg:
                module_models = [
                    x[0] for x in inspect.getmembers(mudule, inspect.isclass)
                ]
            else:
                try:
                    module_models = pyclbr.readmodule(path_to_models).keys()
                except (AttributeError, ImportError):
                    logger.warning(
                        f"Unable to read module attributes in {path_to_models}"
                    )
                    continue
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
