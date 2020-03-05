from enum import Enum
from typing import Type, List, Set, Mapping, Tuple, Sequence

from pydantic import Required, create_model
from pydantic.fields import (
    SHAPE_LIST,
    SHAPE_SET,
    SHAPE_MAPPING,
    SHAPE_TUPLE,
    SHAPE_TUPLE_ELLIPSIS,
    SHAPE_SEQUENCE,
)

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

                if t.shape == SHAPE_LIST:
                    _type = List[t.type_]
                elif t.shape == SHAPE_SET:
                    _type = Set[t.type_]
                elif t.shape == SHAPE_MAPPING:
                    _type = Mapping[t.key_field.type_, t.type_]
                elif t.shape == SHAPE_TUPLE:
                    _type = t.type_
                elif t.shape == SHAPE_TUPLE_ELLIPSIS:
                    _type = Tuple[t.type_, ...]
                elif t.shape == SHAPE_SEQUENCE:
                    _type = Sequence[t.type_]
                else:
                    _type = t.type_
                _fields.update({f: (_type, f_def)})

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

    return create_model(
        f"{cls.__name__}Response", __config__=Config, **_fields
    )
