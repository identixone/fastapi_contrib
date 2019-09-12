from typing import Type

from fastapi_contrib.serializers.utils import gen_model, FieldGenerationMode


def patch(cls: Type) -> Type:
    """
    Decorator for `Serializer` classes to handle inheritance from models,
    read- and write-only fields, combining `Meta`s.

    For more info see `gen_model` method.
    :param cls: serializer class (model or regular)
    :return: wrapped class, which is newly generated pydantic's `BaseModel`
    """
    return gen_model(cls, mode=FieldGenerationMode.REQUEST)
