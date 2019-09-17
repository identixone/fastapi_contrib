import hashlib
import os

from fastapi_contrib.common.utils import resolve_dotted_path
from fastapi_contrib.conf import settings


def get_token_model():
    """
    Gets token model class based on project settings.
    :return: Token (defualt or custom) model class
    """
    return resolve_dotted_path(settings.token_model)


def get_user_model():
    """
    Gets user model class based on project settings.
    :return: User (defualt or custom) model class
    """
    return resolve_dotted_path(settings.user_model)


def default_token_generator() -> str:
    """
    Generates token based on random 64-bits and BLAKE2B hashing algorithm.
    :return: string with generated token
    """
    result = hashlib.blake2b(os.urandom(64))
    return result.hexdigest()


def generate_token() -> str:
    """
    Gets token generator function and invokes it for creation of new token.
    :return: string with generated token
    """
    token_generator = resolve_dotted_path(settings.token_generator)
    return token_generator()
