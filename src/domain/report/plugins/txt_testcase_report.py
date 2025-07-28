import yaml  # type: ignore

from .i_report_formatter import (
    IReportFormatter,
    ReportTypeNotSupportedError,
    ReportFormatterError,
)
from src.dtos import (
    TestReportDTO,
    TestCaseReportDTO,
    ReportArtifactFormat,
    ReportArtifact,
    ReportType,
)


class TxtTestCaseReportFormatter(IReportFormatter):
    """
    Txt-based testcase report with diff, details but without specifications
    """

    @property
    def artifact_format(self) -> ReportArtifactFormat:
        return ReportArtifactFormat.TXT

    @property
    def report_artifact(self) -> ReportArtifact:
        return ReportArtifact.REPORT

    @property
    def report_type(self) -> ReportType:
        return ReportType.TESTCASE

    def create_artifact(self, report: TestReportDTO) -> bytes:
        """
        Creates a txt-based testcase report artifact without specifications.
        """

        if not isinstance(report, TestCaseReportDTO):
            raise ReportTypeNotSupportedError(f"Txt format not supported for {report}")

        # TODO: this is done as a first simple implementation.
        # Add specifications information to the report.
        # exclude specifications to avoid yaml formatting issue
        exclude = {"specifications", "diff"}

        # exclude specifications to avoid yaml formatting issue
        content_dict = report.to_dict(exclude=exclude, mode="json")
        try:
            yaml_bytes = yaml.safe_dump(
                data=content_dict, default_flow_style=False, indent=4, encoding="utf-8"
            )
            return yaml_bytes
        except Exception as e:
            msg = f"Failed to convert dict to yaml bytes: {e}"
            raise ReportFormatterError(msg) from e
