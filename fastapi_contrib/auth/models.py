from datetime import datetime
from pydantic import constr, validator
from pymongo import IndexModel, ASCENDING

from fastapi_contrib.auth.utils import generate_token
from fastapi_contrib.db.models import MongoDBTimeStampedModel


class User(MongoDBTimeStampedModel):
    """
    Default User model that has only `username` field
    on top of default (id, created) pair from `MongoDBTimeStampedModel`
    """
    username: str
    # todo: optional email dependency
    # todo: pwd with configurable hash function

    class Meta:
        collection = "users"


class Token(MongoDBTimeStampedModel):
    """
    Default Token model with several fields implemented as a default:
        * id - inherited from `MongoDBTimeStampedModel`
        * created - inherited from `MongoDBTimeStampedModel`
        * key - string against which user will be authenticated
        * user_id - id of `User`, who owns this token
        * expires - datetime when this token no longer active
        * is_active - defines whether this token can be used
    """
    key: constr(max_length=128) = None
    user_id: int = None
    expires: datetime = None
    is_active: bool = True

    @validator("key", pre=True, always=True)
    def set_key(cls, v, values, **kwargs) -> str:
        """
        If key is supplied (ex. from DB) then use it, otherwise generate new.
        """
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
