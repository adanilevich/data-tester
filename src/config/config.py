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

    # GCP DEPLOYMENT CONFIGURATIONS
    DATATESTER_GCP_PROJECT: str | None = Field(default=None)
    DATATESTER_USE_GCS_STORAGE: bool = Field(default=False)

    # DATA PLATTFORM CONFIGURATION
    DATATESTER_DATA_PLATFORM: str = Field(default="DUMMY")

    # NOTIFIERS CONFIGURATION
    DATATESTER_NOTIFIERS: List[str] = Field(default=["IN_MEMORY", "STDOUT"])

    # CONFIGRATION OF USER STORAGE
    DATATESTER_USER_STORAGE_ENGINE: str = Field(default="LOCAL")

    # CONFIGURATION OF INTERNAL STORAGE
    DATATESTER_INTERNAL_STORAGE_ENGINE: str = Field(default="DICT")  # GCS, LOCAL or other

    DATATESTER_DOMAIN_CONFIGS_LOCATION: str = Field(default="dict://domain_configs/")
    DATATESTER_INTERNAL_TESTRUN_LOCATION: str = Field(default="dict://testruns/")
    DATATESTER_INTERNAL_TESTREPORT_LOCATION: str = Field(default="dict://reports/")
    DATATESTER_INTERNAL_TESTSET_LOCATION: str = Field(default="dict://testsets/")

    def model_post_init(self, __context) -> None:
        """Set config values for local mode"""
        if self.DATATESTER_ENV == "LOCAL":
            # in local mode, we use a dict storage for internal storage
            self.DATATESTER_INTERNAL_STORAGE_ENGINE = "DICT"
            self.DATATESTER_INTERNAL_TESTRUN_LOCATION = "dict://testruns/"
            self.DATATESTER_INTERNAL_TESTREPORT_LOCATION = "dict://reports/"
            self.DATATESTER_INTERNAL_TESTSET_LOCATION = "dict://testsets/"
            self.DATATESTER_DOMAIN_CONFIGS_LOCATION = "dict://domain_configs/"

            # in local mode, we use simple notifiers
            self.DATATESTER_NOTIFIERS = ["IN_MEMORY", "STDOUT"]
