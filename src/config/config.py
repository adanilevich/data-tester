import os
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings

from src.dtos import ReportArtifactFormat

def env(name: str) -> str | None:
    return os.environ.get(name, None)


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

    # DOMAIN CONFIG CONFIGURATION
    DATATESTER_DOMAIN_CONFIGS_LOCATION: str | None = Field(default=None)

    # CONFIGURATION OF INTERNAL STORAGE
    INTERNAL_STORAGE_ENGINE: str = Field(default="DICT")  # GCS, LOCAL or other

    # CONFIGURATION OF INTERNAL STORAGES
    INTERNAL_TESTRUN_LOCATION: str | None = Field(default="dict://testruns/")
    INTERNAL_TESTREPORT_FORMAT: ReportArtifactFormat = ReportArtifactFormat.JSON
    INTERNAL_TESTREPORT_LOCATION: str | None = Field(default="dict://reports/")

    # CONFIGURATION OF USER-FACING TESTREPORT STORAGE
    # This report artifacts will be created by default for testrun reports
    TESTRUN_REPORT_ARTIFACT_FORMAT: ReportArtifactFormat = ReportArtifactFormat.XLSX
    # This artifact will be created for tescase reports
    TESTCASE_REPORT_ARTIFACT_FORMAT: ReportArtifactFormat = ReportArtifactFormat.TXT
    # This artifact will be created for testcase diffs
    TESTCASE_DIFF_ARTIFACT_FORMAT: ReportArtifactFormat = ReportArtifactFormat.XLSX
