from abc import ABC
from typing import Iterable, List

from pydantic import BaseModel
from pymongo.results import UpdateResult

from fastapi_contrib.db.models import MongoDBModel


class AbstractMeta(ABC):
    exclude: set = set()
    model: MongoDBModel = None
    write_only_fields: set = set()
    read_only_fields: set = set()


class Serializer(BaseModel):
    """
    Base Serializer class.

    Almost ALWAYS should be used in conjunction with
    `fastapi_contrib.serializers.openapi.patch` decorator to correctly handle
    inherited model fields and OpenAPI Schema generation with `response_model`.

    Responsible for sanitizing data & converting JSON to & from MongoDBModel.

    Contains supplemental function, related to MongoDBModel,
    mostly proxied to corresponding functions inside model (ex. save, update)

    Heavily uses `Meta` class for fine-tuning input & output. Main fields are:
        * exclude - set of fields that are excluded when serializing to dict
                    and sanitizing list of dicts
        * model - class of the MongoDBModel to use, inherits fields from it
        * write_only_fields - set of fields that can be accepted in request,
                              but excluded when serializing to dict
        * read_only_fields - set of fields that cannot be accepted in request,
                              but included when serializing to dict

    Example usage:

    .. code-block:: python

        app = FastAPI()


        class SomeModel(MongoDBModel):
            field1: str


        @openapi.patch
        class SomeSerializer(Serializer):
            read_only1: str = "const"
            write_only2: int
            not_visible: str = "42"

            class Meta:
                model = SomeModel
                exclude = {"not_visible"}
                write_only_fields = {"write_only2"}
                read_only_fields = {"read_only1"}


        @app.get("/", response_model=SomeSerializer.response_model)
        async def root(serializer: SomeSerializer):
            model_instance = await serializer.save()
            return model_instance.dict()

    POST-ing to this route following JSON:

    .. code-block:: json

        {"read_only1": "a", "write_only2": 123, "field1": "b"}

    Should return following response:

    .. code-block:: json

        {"id": 1, "field1": "b", "read_only1": "const"}

    """

    @classmethod
    def sanitize_list(cls, iterable: Iterable) -> List[dict]:
        """
        Sanitize list of rows that comes from DB to not include `exclude` set.

        :param iterable: sequence of dicts with model fields (from rows in DB)
        :return: list of cleaned, without `excluded`, dicts with model rows
        """

        def clean_d(d):
            if hasattr(cls.Meta, "exclude"):
                for e in cls.Meta.exclude:
                    d.pop(e, None)
                return d
            return d

        return list(map(lambda x: clean_d(x), iterable))

    async def save(
        self,
        include: set = None,
        exclude: set = None,
        rewrite_fields: dict = None,
    ) -> MongoDBModel:
        """
        If we have `model` attribute in Meta, it populates model with data
        and saves it in DB, returning instance of model.

        :param rewrite_fields: dict of fields with values that override any
                other values for these fields right before inserting into DB.
                This is useful when you need to set some value explicitly
                based on request (e.g. user or token).
        :param include: fields to include from model in DB insert command
        :param exclude: fields to exclude from model in DB insert command
        :return: model (MongoDBModel) that was saved
        """
        if (
            hasattr(self, "Meta")
            and getattr(self.Meta, "model", None) is not None
        ):
            instance = self.Meta.model(**self.__dict__)
            await instance.save(
                include=include, exclude=exclude, rewrite_fields=rewrite_fields
            )
            return instance

    async def update_one(
        self,
        filter_kwargs: dict,
        skip_defaults: bool = True,
        array_fields: list = None,
    ) -> UpdateResult:
        """
        If we have `model` attribute in Meta, it proxies filters & update data
        and after that returns actual result of update operation.

        :return: result of update operation
        """
        if (
            hasattr(self, "Meta")
            and getattr(self.Meta, "model", None) is not None
        ):
            data = {}
            fields = self.dict(skip_defaults=skip_defaults)

            if not array_fields:
                array_fields = []

            if array_fields:
                tmp_data = {}
                for i in array_fields:
                    tmp_data[i] = {"$each": fields.pop(i)}
                data.update({"$push": tmp_data})
            if fields:
                data.update({"$set": fields})
            return await self.Meta.model.update_one(
                filter_kwargs=filter_kwargs, **data
            )

    async def update_many(
        self,
        filter_kwargs: dict,
        skip_defaults: bool = True,
        array_fields: list = None,
    ) -> UpdateResult:
        """
        If we have `model` attribute in Meta, it proxies filters & update data
        and after that returns actual result of update operation.

        :return: result of update many operation
        """
        if (
            hasattr(self, "Meta")
            and getattr(self.Meta, "model", None) is not None
        ):
            data = {}
            fields = self.dict(skip_defaults=skip_defaults)

            if not array_fields:
                array_fields = []

            if array_fields:
                tmp_data = {}
                for i in array_fields:
                    tmp_data[i] = {"$each": fields.pop(i)}
                data.update({"$push": tmp_data})
            if fields:
                data.update({"$set": fields})
            return await self.Meta.model.update_many(
                filter_kwargs=filter_kwargs, **data
            )

    def dict(self, *args, **kwargs) -> dict:
        """
        Removes excluded fields based on `Meta` and `kwargs`
        :return: dict of serializer data fields
        """
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
    """
    Left as a proxy for correct naming until we figure out how to inherit
    all the specific to model-handling methods and fields directly in here.
    """

    ...
