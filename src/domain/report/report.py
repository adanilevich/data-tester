from typing import Dict, List, Tuple, cast

from src.domain.report.plugins import ITestCaseFormatter, ITestRunFormatter
from src.dtos import (
    ObjectType,
    ReportArtifact,
    ReportArtifactFormat,
    TestCaseDTO,
    TestRunDTO,
)
from src.infrastructure_ports import IDtoStorage


class ReportError(Exception):
    """Exception raised when a report operation fails."""


class NoFormatterFoundError(ReportError):
    """Exception raised when no formatter is found for a given artifact and format."""


class Report:
    """Creates report artifacts from persisted TestCaseDTO or TestRunDTO objects."""

    def __init__(
        self,
        testcase_formatters: List[ITestCaseFormatter],
        testrun_formatters: List[ITestRunFormatter],
        dto_storage: IDtoStorage,
    ):
        self.dto_storage = dto_storage

        self._testcase_formatters: Dict[
            Tuple[ReportArtifact, ReportArtifactFormat], ITestCaseFormatter
        ] = {}
        for formatter in testcase_formatters:
            key = (formatter.artifact, formatter.artifact_format)
            if key in self._testcase_formatters:
                raise ReportError(f"Formatter {formatter} already registered")
            self._testcase_formatters[key] = formatter

        self._testrun_formatters: Dict[ReportArtifactFormat, ITestRunFormatter] = {}
        for formatter in testrun_formatters:
            if formatter.artifact_format in self._testrun_formatters:
                raise ReportError(f"Formatter {formatter} already registered")
            self._testrun_formatters[formatter.artifact_format] = formatter

    def create_testcase_report_artifact(
        self,
        testcase_id: str,
        artifact: ReportArtifact,
        artifact_format: ReportArtifactFormat,
    ) -> bytes:
        """Loads a TestCaseDTO from storage and creates the requested artifact."""
        key = (artifact, artifact_format)
        formatter = self._testcase_formatters.get(key)
        if formatter is None:
            raise NoFormatterFoundError(
                f"Formatter for {artifact}/{artifact_format} not registered"
            )
        testcase = cast(
            TestCaseDTO,
            self.dto_storage.read_dto(ObjectType.TESTCASE, testcase_id),
        )
        return formatter.create_artifact(testcase)

    def create_testrun_report_artifact(
        self,
        testrun_id: str,
        artifact_format: ReportArtifactFormat,
    ) -> bytes:
        """Loads a TestRunDTO from storage and creates the requested artifact."""
        formatter = self._testrun_formatters.get(artifact_format)
        if formatter is None:
            raise NoFormatterFoundError(
                f"Formatter for {artifact_format} not registered"
            )
        testrun = cast(
            TestRunDTO,
            self.dto_storage.read_dto(ObjectType.TESTRUN, testrun_id),
        )
        return formatter.create_artifact(testrun)
