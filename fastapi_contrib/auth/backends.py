from typing import Optional, Tuple

from fastapi.security.utils import get_authorization_scheme_param
from starlette.authentication import AuthenticationBackend, AuthenticationError
from starlette.requests import HTTPConnection

from fastapi_contrib.auth.utils import get_token_model, get_user_model
from fastapi_contrib.common.utils import get_now

Token = get_token_model()
User = get_user_model()


class AuthBackend(AuthenticationBackend):
    """
    Own Auth Backend based on Starlette's AuthenticationBackend.

    Use instance of this class as `backend` argument to `add_middleware` func:

    .. code-block:: python

        app = FastAPI()

        @app.on_event('startup')
        async def startup():
            app.add_middleware(AuthenticationMiddleware, backend=AuthBackend())

    """

    async def authenticate(
        self, conn: HTTPConnection
    ) -> Tuple[bool, Optional[User]]:
        """
        Main function that AuthenticationMiddleware uses from this backend.
        Should return whether request is authenticated based on credentials and
        if it was, return also user instance.

        :param conn: HTTPConnection of the current request-response cycle
        :return: 2-tuple: is authenticated & user instance if exists
        """
        authorization: str = conn.headers.get("Authorization")
        if not authorization:
            return False, None
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            raise AuthenticationError("Not authenticated")
        if scheme.lower() != "token":
            raise AuthenticationError("Invalid authentication credentials")

        token = await Token.get(
            key=credentials,
            is_active=True,
            expires={"$not": {"$lt": get_now()}},
        )
        if token is None:
            return False, None
        conn.scope["token"] = token

        user = await User.get(id=token.user_id)
        if user is None:
            return False, None

        return True, user
