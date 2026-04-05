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
    DATATESTER_NOTIFIERS: List[str] = Field(default_factory=lambda: ["IN_MEMORY", "LOG"])

    # LOGGING CONFIGURATION
    DATATESTER_LOG_LEVEL: str = Field(default="INFO")
    DATATESTER_LOG_FORMAT: str = Field(default="TEXT")

    # STORAGE ENGINES AND LOCATIONS
    DATATESTER_INTERNAL_STORAGE_LOCATION: str = Field(default="memory://datatester/")
    DATATESTER_USER_STORAGE_ENGINE: str = Field(default="MEMORY")

    # DEMO BACKEND DATA PATHS
    DATATESTER_DEMO_RAW_PATH: str = Field(default="tests/fixtures/demo/raw")
    DATATESTER_DEMO_DB_PATH: str = Field(default="tests/fixtures/demo/dbs")

    # EXECUTION CONFIGURATION
    DATATESTER_MAX_TESTRUN_THREADS: int = Field(default=4)

    # GCP DEPLOYMENT CONFIGURATIONS
    DATATESTER_GCP_PROJECT: str | None = Field(default=None)
