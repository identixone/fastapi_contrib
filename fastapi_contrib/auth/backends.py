from fastapi.security.utils import get_authorization_scheme_param
from starlette.authentication import AuthenticationBackend, AuthenticationError
from starlette.requests import HTTPConnection

from fastapi_contrib.auth.utils import get_token_model, get_user_model


class AuthBackend(AuthenticationBackend):
    async def authenticate(self, conn: HTTPConnection):
        authorization: str = conn.headers.get("Authorization")
        if not authorization:
            return False, None
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            raise AuthenticationError("Not authenticated")
        if scheme.lower() != "token":
            raise AuthenticationError("Invalid authentication credentials")

        Token = get_token_model()
        token = await Token.get(key=credentials)
        if token is None:
            return False, None
        conn.scope["token"] = token

        User = get_user_model()
        user = await User.get(id=token.user_id)
        if user is None:
            return False, None

        return True, user
