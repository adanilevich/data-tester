from io import BytesIO

import polars as pl

from src.dtos import (
    ReportArtifactFormat,
    TestRunDTO,
)

from .i_report_formatter import (
    ITestRunFormatter,
    ReportFormatterError,
)


class XlsxTestRunReportFormatter(ITestRunFormatter):
    """Excel-based testrun report with only most important info included."""

    @property
    def artifact_format(self) -> ReportArtifactFormat:
        return ReportArtifactFormat.XLSX

    def create_artifact(self, testrun: TestRunDTO) -> bytes:
        """Creates a xlsx-based testrun report."""
        rows = [
            {
                "domain": tc.domain,
                "stage": tc.stage,
                "instance": tc.instance,
                "testobject": tc.testobject.name,
                "testtype": tc.testtype.value,
                "result": tc.result.value,
                "summary": tc.summary,
            }
            for tc in testrun.results
        ]

        try:
            df = pl.DataFrame(rows)
            excel_io = BytesIO()
            df.write_excel(excel_io)
            return excel_io.getvalue()
        except Exception as e:
            msg = f"Failed to convert dict to excel bytes: {e}"
            raise ReportFormatterError(msg) from e
