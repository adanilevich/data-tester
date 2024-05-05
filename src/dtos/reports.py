from typing import Dict, List, Self
from uuid import uuid4
from enum import Enum
from datetime import datetime

from pydantic import Field, UUID4, Base64Str

from src.dtos import (
    DTO,
    TestResult,
    TestType,
    TestObjectDTO,
    TestCaseResultDTO,
    TestRunResultDTO,
)


class ArtifactTag(Enum):
    storage = "storage"
    ui = "ui"


class ArtifactType(Enum):
    JSON_TESTCASE_REPORT = "json-testcase-report"
    XLSX_TESTRUN_REPORT = "xlsx-testrun-report"
    XLSX_TESTCASE_DIFF = "xlsx-testcase-diff"
    TXT_TESTCASE_REPORT = "txt-testcase-report"


class ReportArtifactDTO(DTO):
    """
    Report artifacts are files (or other objects) which are viewable and downloadable
    by the user, e.g. for a testrun report an 'xlsx' file containing results for
    all testcases as rows. Report artifacts are normally created by ReportFormatters
    based on the conventions of the specific project.
    """

    id: UUID4 = Field(default_factory=uuid4)
    """A uuid which uniquely identifies the report artifact"""
    artifact_type: ArtifactType
    """E.g.'txt-testcase-report' or 'xlsx-testcase-diff'. Must be unique in one report."""
    sensitive: bool
    """Some artifacts contain sensitive data, e.g. compare sample diffs"""
    url: str | None = Field(default=None)
    """Artifact storage url (e.g. in S3), if applicable."""
    location: str | None = Field(default=None)
    """Artifact location, interpretable by IStorage. E.g. s3://my-bucket/file.txt"""
    content_type: str
    """Https content type of content in 'content_b64', e.g. 'text/plain'"""
    content_b64_str: Base64Str
    """Content of the artifact, enconded as Base64 string """
    filename: str | None = Field(default=None)
    """Filename of artifact, if storeable (see tags 'store')"""
    testrun_id: UUID4
    """Id of corresponding test run"""
    start_ts: datetime
    """Start timestamp of test run or test case which produced the artifact"""
    result: TestResult
    """Result of test run or test case which produced the artifact"""
    tags: List[ArtifactTag]
    """
    List of tags - used to request artifact creation, storage or retrieval by clients:
        'ui': Artifacts exposed to web clients and UIs, e.g. json-based reports.
        'storage': Artifacts created for storage (e.g. on disc, database, etc.). Excel-
            based diffs which are used by users are one example; These can be exposed
            to UIs, e.g. via UI 'download' functions
    """
    # TODO: implement validations between 'store' tags, location, filename and url


class TestCaseReportArtifactDTO(ReportArtifactDTO):
    """
    Extends ReportArtifact by testcase-specific fields.
    """

    testobject: TestObjectDTO
    testcase: TestType
    testcase_id: UUID4

    @classmethod
    def from_result(
        cls,
        result: TestCaseResultDTO,
        artifact_type: ArtifactType,
        content_type: str,
        sensitive: bool,
        content_b64_str: Base64Str,
        filename: str,
        tags: List[ArtifactTag],
    ) -> Self:
        return cls(
            artifact_type=artifact_type,
            content_type=content_type,
            sensitive=sensitive,
            content_b64_str=content_b64_str,
            filename=filename,
            tags=tags,
            testrun_id=result.testrun_id,
            testcase_id=result.testcase_id,
            result=result.result,
            start_ts=result.start_ts,
            testobject=result.testobject,
            testcase=result.testtype,
        )


class TestRunReportArtifactDTO(ReportArtifactDTO):
    """
    Extends ReportArtifact by testrun specific fields
    """

    @classmethod
    def from_result(
        cls,
        result: TestRunResultDTO,
        artifact_type: ArtifactType,
        content_type: str,
        sensitive: bool,
        content_b64_str: Base64Str,
        filename: str,
        tags: List[ArtifactTag],
    ) -> Self:
        return cls(
            artifact_type=artifact_type,
            content_type=content_type,
            sensitive=sensitive,
            content_b64_str=content_b64_str,
            filename=filename,
            tags=tags,
            testrun_id=result.testrun_id,
            result=result.result,
            start_ts=result.start_ts,
        )


class ReportDTO(DTO):
    """
    Base class for testreports. Contains common information which is re-used between
    testcase reports and testrun reports. Also contains report artifacts.
    """

    testrun_id: UUID4
    start_ts: datetime
    end_ts: datetime
    result: TestResult
    artifacts: Dict[str, ReportArtifactDTO] = Field(default={})
    """Artifacts, stored in a dict using artifact.artifact_type as key"""


class TestCaseReportDTO(ReportDTO):
    """
    Contains the relevant testcase execution information for clients and artifacts.
    """

    testcase_id: UUID4
    testobject: TestObjectDTO
    testcase: TestType


class TestRunReportDTO(ReportDTO):
    """
    Contains information on testrun executions.
    """
