import hashlib
import os

from datetime import datetime
from pymongo import IndexModel, ASCENDING
from pydantic import EmailStr, constr, validator

from fastapi_contrib.db.models import MongoDBTimeStampedModel


class User(MongoDBTimeStampedModel):
    email: EmailStr

    class Meta:
        collection = "users"


class Token(MongoDBTimeStampedModel):
    key: constr(max_length=128) = None
    user_id: int = None
    expires: datetime = None
    is_active: bool = True

    @classmethod
    def generate_key(cls):
        result = hashlib.blake2b(os.urandom(64))
        return result.hexdigest()

    @validator("key", pre=True, always=True)
    def set_key(cls, v, values, **kwargs):
        if v:
            return v
        return cls.generate_key()

    class Meta:
        collection = "tokens"
        indexes = [
            IndexModel(
                [("expires", ASCENDING)],
                name="TokenIndex",
                expireAfterSeconds=86400,  # TODO: 1 day seconds (settings?)
            )
        ]
