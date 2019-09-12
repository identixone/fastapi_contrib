from typing import Type

from fastapi_contrib.serializers.utils import gen_model, FieldGenerationMode


def patch(cls: Type) -> Type:
    return gen_model(cls, mode=FieldGenerationMode.REQUEST)
