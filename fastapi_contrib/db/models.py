from datetime import datetime
from typing import List, Optional

from pydantic import validator, BaseModel
from pymongo.results import UpdateResult, DeleteResult

from fastapi_contrib.common.utils import async_timing, get_now
from fastapi_contrib.db.utils import get_db_client, get_next_id


class NotSet(object):
    ...


notset = NotSet()


class MongoDBModel(BaseModel):
    """
    Base Model to use for any information saving in MongoDB.
    Provides `id` field as a base, populated by id-generator.
    Use it as follows:

    .. code-block:: python

        class MyModel(MongoDBModel):
            additional_field1: str
            optional_field2: int = 42

            class Meta:
                collection = "mymodel_collection"


        mymodel = MyModel(additional_field1="value")
        mymodel.save()

        assert mymodel.additional_field1 == "value"
        assert mymodel.optional_field2 == 42
        assert isinstance(mymodel.id, int)

    """

    id: int = None

    @validator("id", pre=True, always=True)
    def set_id(cls, v, values, **kwargs) -> int:
        """
        If id is supplied (ex. from DB) then use it, otherwise generate new.
        """
        if v:
            return v

        return get_next_id()

    @classmethod
    def get_db_collection(cls) -> str:
        return cls.Meta.collection

    @classmethod
    @async_timing
    async def get(cls, **kwargs) -> Optional["MongoDBModel"]:
        db = get_db_client()
        result = await db.get(cls, **kwargs)
        if not result:
            return None

        result["id"] = result.pop("_id")
        return cls(**result)

    @classmethod
    @async_timing
    async def delete(cls, **kwargs) -> DeleteResult:
        db = get_db_client()
        result = await db.delete(cls, **kwargs)
        return result

    @classmethod
    @async_timing
    async def count(cls, **kwargs) -> int:
        db = get_db_client()
        result = await db.count(cls, **kwargs)
        return result

    @classmethod
    @async_timing
    async def list(cls, raw=True, _limit=0, _offset=0, _sort=None, **kwargs):
        db = get_db_client()
        cursor = db.list(
            cls, _limit=_limit, _offset=_offset, _sort=_sort, **kwargs
        )

        result = []
        async for document in cursor:
            document["id"] = document.pop("_id")
            result.append(document)

        if not raw:
            return (cls(**record) for record in result)

        return result

    @async_timing
    async def save(
        self,
        include: set = None,
        exclude: set = None,
        rewrite_fields: dict = None,
    ) -> int:
        db = get_db_client()

        if not rewrite_fields:
            rewrite_fields = {}

        for field, value in rewrite_fields.items():
            setattr(self, field, value)

        insert_result = await db.insert(self, include=include, exclude=exclude)
        self.id = insert_result.inserted_id
        return self.id

    @classmethod
    @async_timing
    async def update_one(cls, filter_kwargs: dict, **kwargs) -> UpdateResult:
        db = get_db_client()
        result = await db.update_one(
            cls, filter_kwargs=filter_kwargs, **kwargs
        )
        return result

    @classmethod
    @async_timing
    async def update_many(cls, filter_kwargs: dict, **kwargs) -> UpdateResult:
        db = get_db_client()
        result = await db.update_many(
            cls, filter_kwargs=filter_kwargs, **kwargs
        )
        return result

    @classmethod
    @async_timing
    async def create_indexes(cls) -> Optional[List[str]]:
        if hasattr(cls.Meta, "indexes"):
            db = get_db_client()
            collection = db.get_collection(cls.Meta.collection)
            return await collection.create_indexes(cls.Meta.indexes)

    class Config:
        anystr_strip_whitespace = True


class MongoDBTimeStampedModel(MongoDBModel):
    """
    TimeStampedModel to use when you need to have `created` field,
    populated at your model creation time.

    Use it as follows:

    .. code-block:: python

        class MyTimeStampedModel(MongoDBTimeStampedModel):

            class Meta:
                collection = "timestamped_collection"


        mymodel = MyTimeStampedModel()
        mymodel.save()

        assert isinstance(mymodel.id, int)
        assert isinstance(mymodel.created, datetime)
    """

    created: datetime = None

    @validator("created", pre=True, always=True)
    def set_created_now(cls, v: datetime) -> datetime:
        """
        If created is supplied (ex. from DB) -> use it, otherwise generate new.
        """
        if v:
            return v
        return get_now()
