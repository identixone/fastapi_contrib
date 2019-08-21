from fastapi.security.utils import get_authorization_scheme_param
from starlette.authentication import AuthenticationBackend, AuthenticationError

from fastapi_contrib.auth.models import Token, User


class AuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        authorization: str = conn.headers.get("Authorization")
        if not authorization:
            return False, None
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            raise AuthenticationError("Not authenticated")
        if scheme.lower() != "token":
            raise AuthenticationError("Invalid authentication credentials")
        token = await Token.get(key=credentials)
        if token is None:
            return False, None
        conn.scope["token"] = token
        user = await User.get(id=token.user_id)
        if user is None:
            return False, None
        return True, user
