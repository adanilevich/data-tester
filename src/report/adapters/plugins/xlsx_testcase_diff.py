from io import BytesIO

import polars as pl
import xlsxwriter  # type: ignore

from src.report.ports.plugins import (
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


class XlsxTestCaseDiffFormatter(IReportFormatter):
    """
    Excel-based diff of a compare testcase
    """

    @property
    def artifact_format(self) -> ReportArtifactFormat:
        return ReportArtifactFormat.XLSX

    @property
    def report_artifact(self) -> ReportArtifact:
        return ReportArtifact.DIFF

    @property
    def report_type(self) -> ReportType:
        return ReportType.TESTCASE

    def create_artifact(self, report: TestReportDTO) -> bytes:
        """Creates a xlsx-based diff of a testcase with all diffs as separate sheets"""

        if not isinstance(report, TestCaseReportDTO):
            raise ReportTypeNotSupportedError(f"Xlsx diff not supported for {report}")

        if len(report.diff) == 0:
            raise ReportFormatterError("No diff to create artifact for")

        excel_io = BytesIO()
        workbook = xlsxwriter.Workbook(excel_io)

        for key, value in report.diff.items():
            df = pl.DataFrame(value)
            worksheet = workbook.add_worksheet(key)

            df.write_excel(workbook=workbook, worksheet=worksheet)

        workbook.close()
        return excel_io.getvalue()
