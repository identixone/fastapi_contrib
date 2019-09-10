from pydantic import BaseSettings
from typing import List

__all__ = ["settings"]


class Settings(BaseSettings):
    logger: str = "logging"
    debug_timing: bool = False
    request_id_header: str = "Request-ID"

    mongodb_dsn: str = "mongodb://example:pwd@localhost:27017"
    mongodb_dbname: str = "default"
    mongodb_id_generator: str = "fastapi_contrib.db.utils.default_id_generator"

    now_function: str = None  # "pytz.now" or any other custom function path

    fastapi_app: str  # e.g. "project.server.app" this is where app = FastAPI()

    project_root: str  # os.path.abspath(__file__), apps/ should be inside dir

    user_model: str = "fastapi_contrib.auth.models.User"
    token_model: str = "fastapi_contrib.auth.models.Token"
    token_generator: str = "fastapi_contrib.auth.utils.default_token_generator"

    apps: List[str] = []
    apps_folder_name: str = "apps"

    class Config:
        env_prefix = "CONTRIB_"


settings = Settings()
