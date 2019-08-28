from pymongo.collection import Collection
from pymongo.results import InsertOneResult, DeleteResult

from fastapi_contrib.db.models import MongoDBModel
from fastapi_contrib.common.utils import get_current_app


class MongoDBClient(object):
    """
    Singleton. TODO: Singleton base (abc?) class
    """

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            app = get_current_app()
            cls.__instance.mongodb = app.mongodb
        return cls.__instance

    def get_collection(self, collection_name: str) -> Collection:
        return getattr(self.mongodb, collection_name)

    async def insert(
        self, model: MongoDBModel, session=None, include=None, exclude=None
    ) -> InsertOneResult:
        data = model.dict(include=include, exclude=exclude)
        data["_id"] = data.pop("id")
        collection_name = model.get_db_collection()
        collection = self.get_collection(collection_name)
        return await collection.insert_one(data, session=session)

    async def update(
        self, model: MongoDBModel, session=None, include=None, exclude=None
    ) -> InsertOneResult:
        data = model.dict(include=include, exclude=exclude)
        doc_id = data.pop("id")
        collection_name = model.get_db_collection()
        collection = self.get_collection(collection_name)
        return await collection.update_one({"_id": doc_id}, **data, session=session)
    
    async def count(self, model: MongoDBModel, session=None, **kwargs) -> int:
        _id = kwargs.pop("id", None)
        if _id is not None:
            kwargs["_id"] = _id

        collection_name = model.get_db_collection()
        collection = self.get_collection(collection_name)
        res = await collection.count_documents(kwargs, session=session)
        return res

    async def delete(
        self, model: MongoDBModel, session=None, **kwargs
    ) -> DeleteResult:
        _id = kwargs.pop("id", None)
        if _id is not None:
            kwargs["_id"] = _id

        collection_name = model.get_db_collection()
        collection = self.get_collection(collection_name)
        res = await collection.delete_many(kwargs, session=session)
        return res

    async def get(self, model: MongoDBModel, session=None, **kwargs) -> dict:
        _id = kwargs.pop("id", None)
        if _id is not None:
            kwargs["_id"] = _id

        collection_name = model.get_db_collection()
        collection = self.get_collection(collection_name)
        res = await collection.find_one(kwargs, session=session)
        return res

    def list(
        self, model: MongoDBModel, session=None, _offset=0, _limit=0, **kwargs
    ):
        _id = kwargs.pop("id", None)
        if _id is not None:
            kwargs["_id"] = _id

        collection_name = model.get_db_collection()
        collection = self.get_collection(collection_name)
        return collection.find(
            kwargs, session=session, skip=_offset, limit=_limit
        )
