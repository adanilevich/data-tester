import json

from src.report.ports.plugins import (
    IReportFormatter,
    ReportTypeNotSupportedError,
    ReportFormatterError,
)
from src.dtos import (
    TestReportDTO,
    TestCaseReportDTO,
    TestRunReportDTO,
    ReportArtifactFormat,
    ReportArtifact,
    ReportType,
)


class JsonTestCaseReportFormatter(IReportFormatter):
    """
    JSON-based testcase report formatter
    """

    @property
    def artifact_format(self) -> ReportArtifactFormat:
        return ReportArtifactFormat.JSON

    @property
    def report_artifact(self) -> ReportArtifact:
        return ReportArtifact.REPORT

    @property
    def report_type(self) -> ReportType:
        return ReportType.TESTCASE

    def create_artifact(self, report: TestReportDTO) -> bytes:
        """
        Creates a JSON-based testcase report artifact.
        """

        if not isinstance(report, TestCaseReportDTO):
            raise ReportTypeNotSupportedError(f"JSON format not supported for {report}")

        try:
            # Convert to dict with JSON mode for proper serialization
            content_dict = report.to_dict(mode="json")
            json_bytes = json.dumps(content_dict, indent=2, ensure_ascii=False).encode(
                "utf-8"
            )
            return json_bytes
        except Exception as e:
            msg = f"Failed to convert dict to JSON bytes: {e}"
            raise ReportFormatterError(msg) from e


class JsonTestRunReportFormatter(IReportFormatter):
    """
    JSON-based testrun report formatter
    """

    @property
    def artifact_format(self) -> ReportArtifactFormat:
        return ReportArtifactFormat.JSON

    @property
    def report_artifact(self) -> ReportArtifact:
        return ReportArtifact.REPORT

    @property
    def report_type(self) -> ReportType:
        return ReportType.TESTRUN

    def create_artifact(self, report: TestReportDTO) -> bytes:
        """
        Creates a JSON-based testrun report artifact.
        """

        if not isinstance(report, TestRunReportDTO):
            raise ReportTypeNotSupportedError(f"JSON format not supported for {report}")

        try:
            # Convert to dict with JSON mode for proper serialization
            content_dict = report.to_dict(mode="json")
            json_bytes = json.dumps(content_dict, indent=2, ensure_ascii=False).encode(
                "utf-8"
            )
            return json_bytes
        except Exception as e:
            msg = f"Failed to convert dict to JSON bytes: {e}"
            raise ReportFormatterError(msg) from e
