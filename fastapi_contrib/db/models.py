from datetime import datetime
from pydantic import validator, BaseModel

from fastapi_contrib.common.utils import async_timing
from fastapi_contrib.db.utils import get_db_client, get_next_id, get_now


class MongoDBModel(BaseModel):
    id: int = None

    @validator("id", pre=True, always=True)
    def set_id(cls, v, values, **kwargs):
        if "_id" in values and v != values["_id"]:
            return values["_id"]
        if v:
            return v

        return get_next_id()

    @classmethod
    def get_db_collection(cls):
        return cls.Meta.collection

    @classmethod
    @async_timing
    async def get(cls, **kwargs):
        db = get_db_client()
        result = await db.get(cls, **kwargs)
        if not result:
            return None

        result["id"] = result.pop("_id")
        return cls(**result)

    @classmethod
    @async_timing
    async def delete(cls, **kwargs):
        db = get_db_client()
        result = await db.delete(cls, **kwargs)
        return result

    @classmethod
    @async_timing
    async def count(cls, **kwargs):
        db = get_db_client()
        result = await db.count(cls, **kwargs)
        return result

    @classmethod
    @async_timing
    async def list(cls, raw=True, _limit=0, _offset=0, length=100, **kwargs):
        db = get_db_client()
        cursor = db.list(cls, _limit=_limit, _offset=_offset, **kwargs)
        result = await cursor.to_list(length=length)

        for _dict in result:
            _dict.update({"id": _dict.pop("_id")})

        if not raw:
            return (cls(**record) for record in result)

        return result

    @async_timing
    async def save(self, include=None, exclude=None):
        db = get_db_client()
        insert_result = await db.insert(self, include=include, exclude=exclude)
        self.id = insert_result.inserted_id
    
    @async_timing
    async def update(self, include=None, exclude=None):
        db = get_db_client()
        insert_result = await db.update(self, include=include, exclude=exclude)
        self.id = insert_result.inserted_id

    @classmethod
    @async_timing
    async def create_indexes(cls):
        if hasattr(cls.Meta, 'indexes'):
            db = get_db_client()
            collection = db.get_collection(cls.Meta.collection)
            await collection.create_indexes(cls.Meta.indexes)

    class Config:
        anystr_strip_whitespace = True


class MongoDBTimeStampedModel(MongoDBModel):
    created: datetime = None

    @validator("created", pre=True, always=True)
    def set_created_now(cls, v):
        if v:
            return v
        return get_now()
