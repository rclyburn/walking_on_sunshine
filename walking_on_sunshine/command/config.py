from pydantic_settings import BaseSettings

from walking_on_sunshine.api.config import Config as ApiConfig
from walking_on_sunshine.app.config import Config as AppConfig


class RootConfig(BaseSettings):
    app: AppConfig | None = None
    api: ApiConfig | None = None

    class Config:
        env_prefix = "WOS_"
        env_nested_delimiter = ""
