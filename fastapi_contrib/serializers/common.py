from abc import ABC
from typing import Iterable, List, Any

from pydantic import BaseModel
from pymongo.results import UpdateResult

from fastapi_contrib.db.models import MongoDBModel


class AbstractMeta(ABC):
    exclude = set()
    model = None
    write_only_fields = set()
    read_only_fields = set()


class Serializer(BaseModel):
    @classmethod
    def sanitize_list(cls, iterable: Iterable) -> List[dict]:
        def clean_d(d):
            if hasattr(cls.Meta, "exclude"):
                for e in cls.Meta.exclude:
                    d.pop(e, None)
                return d
            return d

        return list(map(lambda x: clean_d(x), iterable))

    async def save(self) -> MongoDBModel:
        if (
            hasattr(self, "Meta")
            and getattr(self.Meta, "model", None) is not None
        ):
            instance = self.Meta.model(**self.__values__)
            await instance.save()
            return instance

    async def update_one(self, filter_kwargs) -> UpdateResult:
        return await self.Meta.model.update_one(
            filter_kwargs=filter_kwargs, **self.dict())

    async def update_many(self, filter_kwargs) -> UpdateResult:
        return await self.Meta.model.update_many(
            filter_kwargs=filter_kwargs, **self.dict())

    def dict(self, *args, **kwargs) -> dict:
        exclude = kwargs.get("exclude")
        if not exclude:
            exclude = set()

        exclude.update({"_id"})

        if hasattr(self.Meta, "exclude") and self.Meta.exclude:
            exclude.update(self.Meta.exclude)

        if (
            hasattr(self.Meta, "write_only_fields")
            and self.Meta.write_only_fields
        ):
            exclude.update(self.Meta.write_only_fields)

        kwargs.update({"exclude": exclude})
        original = super().dict(*args, **kwargs)
        return original

    class Meta(AbstractMeta):
        ...


class ModelSerializer(Serializer):
    ...
