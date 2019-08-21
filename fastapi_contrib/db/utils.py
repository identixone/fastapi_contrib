import importlib
import motor.motor_asyncio
import pkgutil
import pyclbr
import os


def setup_mongodb(app):
    client = motor.motor_asyncio.AsyncIOMotorClient(app.settings.mongodb_dsn)
    app.mongodb = client[app.settings.mongodb_dbname]
    app.mongodb_client = get_db_client(app)


def get_db_client(app=None):
    from fastapi_contrib.db.client import MongoDBClient
    if app:
        client = MongoDBClient(app)
    else:
        client = MongoDBClient()
    return client


def get_models(app):
    from fastapi_contrib.db.models import MongoDBModel

    path = os.path.dirname(os.path.abspath(__file__))
    models = []
    for app in app.settings.apps:
        modules = [f[1] for f in pkgutil.walk_packages(path=[f"{path}/{app}"])]
        if "models" in modules:
            module_models = pyclbr.readmodule(f"apps.{app}.models").keys()
            mudule = importlib.import_module(f"apps.{app}.models")
            models.extend([getattr(mudule, model) for model in module_models])

    return list(filter(lambda x: issubclass(x, MongoDBModel), models))


async def create_indexes(app):
    models = get_models(app)
    for model in models:
        await model.create_indexes()
