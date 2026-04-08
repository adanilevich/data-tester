from abc import ABC, abstractmethod

from src.dtos import ReportArtifact, ReportArtifactFormat, TestCaseDTO, TestRunDTO


class ReportFormatterError(Exception):
    """"""


class ReportTypeNotSupportedError(ReportFormatterError):
    """Raised when a report type is not supported by the formatter."""


class ITestCaseFormatter(ABC):
    """Formats a TestCaseDTO into a report artifact."""

    @property
    @abstractmethod
    def artifact_format(self) -> ReportArtifactFormat:
        """Returns the supported artifact format."""

    @property
    @abstractmethod
    def artifact(self) -> ReportArtifact:
        """Returns the supported artifact type (REPORT or DIFF)."""

    @abstractmethod
    def create_artifact(self, testcase: TestCaseDTO) -> bytes:
        """Creates a formatted artifact from a TestCaseDTO."""


class ITestRunFormatter(ABC):
    """Formats a TestRunDTO into a report artifact."""

    @property
    @abstractmethod
    def artifact_format(self) -> ReportArtifactFormat:
        """Returns the supported artifact format."""

    @abstractmethod
    def create_artifact(self, testrun: TestRunDTO) -> bytes:
        """Creates a formatted artifact from a TestRunDTO."""
