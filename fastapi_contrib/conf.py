import os
from pathlib import Path

from pydantic import BaseSettings
from typing import List, Optional

contrib_secrets_dir: Optional[str] = os.environ.get(
    "CONTRIB_SECRETS_DIR", "/run/secrets"
)
if not Path(contrib_secrets_dir).exists():
    contrib_secrets_dir = None


class Settings(BaseSettings):
    """
    Configuration settings for this library.

    For now you could only change the settings
    via CONTRIB_<ATTRIBUTE_NAME> environment variables.

    :param logger: Dotted path to the logger (using this attribute, standard
                   logging methods will be used: logging.debug(), .info(), etc.
    :param log_level: Standard LEVEL for logging (DEBUG/INFO/WARNING/etc.)
    :param debug_timing: Whether to enable time logging for decorated functions
    :param request_id_header: String name for header, that is expected to have
                              unique request id for tracing purposes.
                              Might go away when we add opentracing here.
    :param mongodb_dsn: DSN connection string to MongoDB
    :param mongodb_dbname: String name of a database to connect to in MongoDB
    :param mongodb_id_generator: Dotted path to the function, which will
                                 be used when assigning IDs for MongoDB records
    :param now_function: Dotted path to the function, which will be used when
                         assigning `created` field for MongoDB records.
                         Should be used throughout the code for consistency.
    :param fastapi_app: Dotted path to the instance of `FastAPI` main app.
    :param user_model: Dotted path to the class, which will be used
                       as the main user model in a project.
    :param token_model: Dotted path to the class, which will be used
                        as the main token model in a project.
    :param token_generator: Dotted path to the function, which will be used
                            when assigning `key` attribute of a token model.
    :param apps: List of app names. For now only needed to detect models inside
                                    them and generate indexes upon startup
                                    (see: `create_indexes`)
    :param apps_folder_name: Name of the folders which contains dirs with apps.
    """
    logger: str = "logging"
    log_level: str = "INFO"
    debug_timing: bool = False
    request_id_header: str = "Request-ID"

    service_name: str = "fastapi_contrib"
    trace_id_header: str = "X-TRACE-ID"
    jaeger_host: str = "jaeger"
    jaeger_port: int = 5775
    jaeger_sampler_type: str = "probabilistic"
    jaeger_sampler_rate: float = 1.0

    mongodb_dsn: str = "mongodb://example:pwd@localhost:27017"
    mongodb_dbname: str = "default"
    mongodb_min_pool_size: int = 0
    mongodb_max_pool_size: int = 100
    mongodb_id_generator: str = "fastapi_contrib.db.utils.default_id_generator"

    now_function: str = None
    TZ: str = "UTC"

    fastapi_app: str = None  # e.g. "project.server.app", where app = FastAPI()

    user_model: str = "fastapi_contrib.auth.models.User"
    token_model: str = "fastapi_contrib.auth.models.Token"
    token_generator: str = "fastapi_contrib.auth.utils.default_token_generator"

    apps: List[str] = []
    apps_folder_name: str = "apps"

    class Config:
        env_prefix = "CONTRIB_"
        secrets_dir = contrib_secrets_dir


# TODO: ability to override this settings class from the actual app
settings = Settings()
