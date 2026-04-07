from io import BytesIO

import polars as pl
import xlsxwriter

from src.dtos import (
    ReportArtifact,
    ReportArtifactFormat,
    TestCaseDTO,
)

from .i_report_formatter import (
    ITestCaseFormatter,
    ReportFormatterError,
)


class XlsxTestCaseDiffFormatter(ITestCaseFormatter):
    """Excel-based diff of a compare testcase."""

    @property
    def artifact_format(self) -> ReportArtifactFormat:
        return ReportArtifactFormat.XLSX

    @property
    def artifact(self) -> ReportArtifact:
        return ReportArtifact.DIFF

    def create_artifact(self, testcase: TestCaseDTO) -> bytes:
        """Creates a xlsx-based diff of a testcase with all diffs as separate sheets."""
        if len(testcase.diff) == 0:
            raise ReportFormatterError("No diff to create artifact for")

        excel_io = BytesIO()
        workbook = xlsxwriter.Workbook(excel_io)

        for key, value in testcase.diff.items():
            df = pl.DataFrame(value)
            worksheet = workbook.add_worksheet(key)
            df.write_excel(workbook=workbook, worksheet=worksheet)

        workbook.close()
        return excel_io.getvalue()
