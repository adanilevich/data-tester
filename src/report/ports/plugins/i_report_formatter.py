from abc import ABC, abstractmethod
from src.dtos import TestReportDTO, ReportArtifactFormat, ReportArtifact, ReportType


class ReportFormatterError(Exception):
    """"""

class ReportTypeNotSupportedError(ReportFormatterError):
    """
    Raised when a report type is not supported by the formatter.
    """


class IReportFormatter(ABC):
    """
    Interface definition for a report formatter. Report formatters operate on Report DTOs
    and serialize the provided report to given format, e.g. JSON, TXT, XLSX.
    Reports artifacts can be both created for testruns and testcases; for testcases
    artifacts can be created for both the report itself and the diff.
    """

    @abstractmethod
    def create_artifact(self, report: TestReportDTO) -> bytes:
        """
        Creates a formatted report artifact for a given report.
        """

    @property
    @abstractmethod
    def artifact_format(self) -> ReportArtifactFormat:
        """
        Returns supported artifact format.
        """

    @property
    @abstractmethod
    def report_artifact(self) -> ReportArtifact:
        """
        Returns supported report artifact type, e.g. 'report' or 'diff'.
        """
    @property
    @abstractmethod
    def report_type(self) -> ReportType:
        """
        Returns supported report type, e.g. 'testcase' or 'testrun'.
        """
