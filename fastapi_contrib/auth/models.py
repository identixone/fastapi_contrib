from datetime import datetime
from pydantic import constr, validator
from pymongo import IndexModel, ASCENDING

from fastapi_contrib.auth.utils import generate_token
from fastapi_contrib.db.models import MongoDBTimeStampedModel


class User(MongoDBTimeStampedModel):
    username: str
    # todo: optional email dependency
    # todo: pwd with configurable hash function

    class Meta:
        collection = "users"


class Token(MongoDBTimeStampedModel):
    key: constr(max_length=128) = None
    user_id: int = None
    expires: datetime = None
    is_active: bool = True

    @validator("key", pre=True, always=True)
    def set_key(cls, v, values, **kwargs) -> str:
        if v:
            return v
        return generate_token()

    class Meta:
        collection = "tokens"
        indexes = [
            IndexModel(
                [("expires", ASCENDING)],
                name="TokenIndex",
                expireAfterSeconds=86400,  # TODO: 1 day seconds (settings?)
            )
        ]
