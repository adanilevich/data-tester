import os

from pydantic import Field
from pydantic_settings import BaseSettings


def env(name: str) -> str | None:
    return os.environ.get(name, None)


class Config(BaseSettings):
    DATATESTER_GCP_PROJECT: str | None = Field(default=None)
    DATATESTER_DOMAIN_CONFIGS_LOCATION: str | None = Field(default=None)
    DATATESTER_ENV: str | None = Field(default=None)
