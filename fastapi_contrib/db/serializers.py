from typing import Iterable, List

from pydantic import BaseModel, create_model


class Serializer(BaseModel):

    @classmethod
    def sanitize_list(cls, iterable: Iterable) -> List[dict]:
        def clean_d(d):
            for e in cls.Meta.exclude:
                d.pop(e)
            return d
        return list(map(lambda x: clean_d(x), iterable))

    async def save(self):
        instance = self.Meta.model(**self.__values__)
        await instance.save()
        self.id = instance.id
        return instance

    async def update_one(self, filter_kwargs: dict = {}):
        instance = self.Meta.model(**self.__values__)
        await instance.update_one(filter_kwargs, self.dict())
        return instance

    def dict(self, *args, **kwargs) -> dict:
        exclude = kwargs.get('exclude')
        if not exclude:
            exclude = set()

        exclude.update({"_id"})

        if hasattr(self.Meta, "exclude"):
            exclude.update(self.Meta.exclude)

        if hasattr(self.Meta, "write_only_fields"):
            exclude.update(self.Meta.write_only_fields)

        kwargs.update({"exclude": exclude})
        original = super().dict(*args, **kwargs)
        return original


class ModelSerializer(Serializer):

    def __new__(cls, *args, **kwargs):
        _fields = {}
        for f, t in cls.Meta.model.__fields__.items():
            if f not in cls.Meta.exclude:
                _fields.update({f: (t.type_, t.default)})
        new_model = create_model(cls.__name__, __base__=Serializer, **_fields)
        new_model.Meta = cls.Meta
        return new_model(*args, **kwargs)
