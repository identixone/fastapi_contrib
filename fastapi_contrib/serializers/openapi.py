from fastapi_contrib.serializers.utils import gen_model, FieldGenerationMode


def patch(cls):
    return gen_model(cls, mode=FieldGenerationMode.REQUEST)
