import time
import random
import sys

from bson import ObjectId
from datetime import datetime
from pydantic import validator, BaseModel
from uuid import uuid4
from fastapi_contrib.db.utils import get_db_client


class MongoDBModel(BaseModel):
    id: int = None

    @validator("id", pre=True, always=True)
    def set_id(cls, v, values, **kwargs):
        if "_id" in values and v != values["_id"]:
            return values["_id"]
        if v:
            return v
        return cls.next_id()

    @classmethod
    def seq_id(cls):
        oid = ObjectId()
        # Last 3 bytes is a counter, starting with a random value.
        # https://docs.mongodb.com/manual/reference/method/ObjectId/
        bytes_counter = oid.binary[:3]
        return int.from_bytes(bytes_counter, byteorder=sys.byteorder)

    @classmethod
    def next_id(cls):
        """
        :return: 64-bit int ID
        """
        bit_size = 64
        unique_id = uuid4().int >> bit_size
        return unique_id

    @classmethod
    def get_db_collection(cls):
        return cls.Meta.collection

    @classmethod
    async def get(cls, **kwargs):
        app = kwargs.pop('app') if 'app' in kwargs else None
        db = get_db_client(app=app)
        result = await db.get(cls, **kwargs)
        if not result:
            return None

        result["id"] = result.pop("_id")
        return cls(**result)

    @classmethod
    async def delete(cls, **kwargs):
        db = get_db_client()
        result = await db.delete(cls, **kwargs)
        return result

    @classmethod
    async def count(cls, **kwargs):
        db = get_db_client()
        result = await db.count(cls, **kwargs)
        return result

    @classmethod
    async def list(cls, raw=True, _limit=0, _offset=0, **kwargs):
        db = get_db_client()
        cursor = db.list(cls, _limit=_limit, _offset=_offset, **kwargs)
        result = await cursor.to_list(length=100)

        for _dict in result:
            _dict.update({"id": _dict.pop("_id")})

        if not raw:
            return (cls(**record) for record in result)

        return result

    async def save(self, include=None, exclude=None):
        db = get_db_client()
        insert_result = await db.insert(self, include=include, exclude=exclude)
        self.id = insert_result.inserted_id

    @classmethod
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
        return datetime.utcnow()
