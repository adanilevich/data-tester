import os

from pydantic import Field
from pydantic_settings import BaseSettings

from src.dtos import ReportArtifactFormat

def env(name: str) -> str | None:
    return os.environ.get(name, None)


class Config(BaseSettings):

    # GCP DEPLOYMENT CONFIGURATIONS
    DATATESTER_GCP_PROJECT: str | None = Field(default=None)
    DATATESTER_USE_GCS_STORAGE: bool = Field(default=False)

    # DOMAIN CONFIG CONFIGURATIONS
    DATATESTER_DOMAIN_CONFIGS_LOCATION: str | None = Field(default=None)
    DATATESTER_ENV: str | None = Field(default=None)

    # CONFIGURATION OF INTERNAL TESTREPORT STORAGE
    INTERNAL_TESTREPORT_FORMAT: ReportArtifactFormat = ReportArtifactFormat.JSON
    # define application-internal location for testreports
    INTERNAL_TESTREPORT_LOCATION: str | None = Field(default=None)

    # CONFIGURATION OF USER-FACING TESTREPORT STORAGE
    # This report artifacts will be created by default for testrun reports
    TESTRUN_REPORT_ARTIFACT_FORMAT: ReportArtifactFormat = ReportArtifactFormat.XLSX
    # This artifact will be created for tescase reports
    TESTCASE_REPORT_ARTIFACT_FORMAT: ReportArtifactFormat = ReportArtifactFormat.TXT
    # This artifact will be created for testcase diffs
    TESTCASE_DIFF_ARTIFACT_FORMAT: ReportArtifactFormat = ReportArtifactFormat.XLSX
