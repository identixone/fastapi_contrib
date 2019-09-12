from enum import Enum
from typing import Type

from pydantic import Required, create_model

from fastapi_contrib.serializers.common import AbstractMeta, Serializer


class FieldGenerationMode(int, Enum):
    """
    Defines modes in which fields of decorated serializer should be generated.
    """
    REQUEST = 1
    RESPONSE = 2


def gen_model(cls: Type, mode: FieldGenerationMode):
    """
    Generate `pydantic.BaseModel` based on fields in Serializer class,
    its Meta class and possible Model class.

    :param cls: serializer class (could be modelserializer or regular one)
    :param mode: field generation mode
    :return: newly generated `BaseModel` from fields in Model & Serializer
    """
    _fields = {}

    _Meta = getattr(cls, "Meta", type("Meta"))
    Meta = type("Meta", (_Meta, AbstractMeta), {})

    Config = getattr(cls, "Config", getattr(Serializer, "Config"))

    if mode == FieldGenerationMode.RESPONSE:
        excluded = Meta.exclude | Meta.write_only_fields
    else:
        excluded = Meta.exclude | Meta.read_only_fields

    if hasattr(Meta, "model") and Meta.model is not None:
        for f, t in Meta.model.__fields__.items():
            if f not in excluded:
                f_def = t.default
                if t.required:
                    f_def = Required
                _fields.update({f: (t.type_, f_def)})

    for f, t in cls.__fields__.items():
        if f not in excluded:
            f_def = t.default
            if t.required:
                f_def = Required
            _fields.update({f: (t.type_, f_def)})

    if mode == FieldGenerationMode.REQUEST:
        response_model = gen_model(cls, mode=FieldGenerationMode.RESPONSE)

        Serializer.Config = Config
        model = create_model(cls.__name__, __base__=Serializer, **_fields)
        setattr(model, "response_model", response_model)
        setattr(model, "Meta", Meta)
        setattr(model, "Config", Config)

        reserved_attrs = ["Meta", "response_model", "Config"]
        for attr, value in cls.__dict__.items():
            if not attr.startswith("_") and attr not in reserved_attrs:
                setattr(model, attr, value)

        return model

    return create_model(f"{cls.__name__}Response", __config__=Config, **_fields)
