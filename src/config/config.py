import os
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings

from src.dtos import ArtifactType

def env(name: str) -> str | None:
    return os.environ.get(name, None)


class Config(BaseSettings):
    DATATESTER_GCP_PROJECT: str | None = Field(default=None)
    DATATESTER_USE_GCS_STORAGE: bool = Field(default=False)
    DATATESTER_DOMAIN_CONFIGS_LOCATION: str | None = Field(default=None)
    DATATESTER_ENV: str | None = Field(default=None)
    """When stored, testreports will be stored in folders defined here"""
    GROUP_TESTREPORTS_BY: List[str] = ["date", "testrun_id"]
    """These report artifacts will be created by default for testrun reports"""
    TESTRUN_REPORT_ARTIFACTS: List[ArtifactType] = [ArtifactType.XLSX_TESTRUN_REPORT]
    """These report artifacts will be created for tescase reports"""
    TESTCASE_REPORT_ARTIFACTS: List[ArtifactType] = [
        ArtifactType.JSON_TESTCASE_REPORT,
        ArtifactType.XLSX_TESTCASE_DIFF,
        ArtifactType.XLSX_TESTRUN_REPORT,
    ]

