import hashlib
import os

from fastapi_contrib.common.utils import resolve_dotted_path
from fastapi_contrib.conf import settings
from fastapi_contrib.db.models import MongoDBModel


def get_token_model() -> MongoDBModel:
    return resolve_dotted_path(settings.token_model)


def get_user_model() -> MongoDBModel:
    return resolve_dotted_path(settings.user_model)


def default_token_generator() -> str:
    result = hashlib.blake2b(os.urandom(64))
    return result.hexdigest()


def generate_token() -> str:
    token_generator = resolve_dotted_path(settings.token_generator)
    return token_generator()
