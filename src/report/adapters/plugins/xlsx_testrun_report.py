from io import BytesIO

import polars as pl

from src.report.ports.plugins import (IReportFormatter, ReportTypeNotSupportedError,
    ReportFormatterError)
from src.dtos import (
    TestReportDTO, TestRunReportDTO, ReportArtifactFormat, ReportArtifact, ReportType
)


class XlsxTestRunReportFormatter(IReportFormatter):
    """
    Excel-based testrun report with only most important info included
    """

    @property
    def artifact_format(self) -> ReportArtifactFormat:
        return ReportArtifactFormat.XLSX

    @property
    def report_artifact(self) -> ReportArtifact:
        return ReportArtifact.REPORT

    @property
    def report_type(self) -> ReportType:
        return ReportType.TESTRUN

    def create_artifact(self, report: TestReportDTO) -> bytes:
        """Creates a xlsx-based testrun report"""

        if not isinstance(report, TestRunReportDTO):
            msg = "Can't create testrun report from a TestCaseReportDTO object"
            raise ReportTypeNotSupportedError(msg)

        testcase_results = [result.to_dict() for result in report.testcase_results]

        try:
            df = pl.DataFrame(testcase_results)
            excel_io = BytesIO()
            df.write_excel(excel_io)
            return excel_io.getvalue()
        except Exception as e:
            msg = f"Failed to convert dict to excel bytes: {e}"
            raise ReportFormatterError(msg) from e
