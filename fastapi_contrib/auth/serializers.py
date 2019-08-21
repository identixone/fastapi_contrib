from fastapi_contrib.auth.models import Token
from fastapi_contrib.db.serializers import ModelSerializer


class TokenSerializer(ModelSerializer):

    class Meta:
        model = Token
        exclude = {"user_id"}
