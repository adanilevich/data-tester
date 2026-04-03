import os
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


def env(name: str) -> str | None:
    return os.environ.get(name, None)


class ConfigError(Exception):
    """
    Exception raised when a config value is not set.
    """


class Config(BaseSettings):
    # ENVIRONMENT CONFIGURATION
    DATATESTER_ENV: str = Field(default="LOCAL")

    # DATA PLATTFORM CONFIGURATION
    DATATESTER_DATA_PLATFORM: str = Field(default="DUMMY")

    # NOTIFIERS CONFIGURATION
    DATATESTER_NOTIFIERS: List[str] = Field(
        default_factory=lambda: ["IN_MEMORY", "STDOUT"]
    )

    # STORAGE ENGINES AND LOCATIONS
    DATATESTER_INTERNAL_STORAGE_LOCATION: str = Field(default="memory://datatester/")
    DATATESTER_USER_STORAGE_ENGINE: str = Field(default="MEMORY")

    # GCP DEPLOYMENT CONFIGURATIONS
    DATATESTER_GCP_PROJECT: str | None = Field(default=None)

    def model_post_init(self, __context) -> None:
        """Set config values for local mode"""
        if self.DATATESTER_ENV == "LOCAL":
            self.DATATESTER_INTERNAL_STORAGE_LOCATION = "memory://datatester/"
            self.DATATESTER_USER_STORAGE_ENGINE = "MEMORY"
            self.DATATESTER_NOTIFIERS = ["IN_MEMORY","STDOUT",]
