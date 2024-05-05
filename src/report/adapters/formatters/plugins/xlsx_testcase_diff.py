from io import BytesIO

import polars as pl

from src.report.adapters.formatters import AbstractArtifactFormatter
from src.dtos import TestResultDTO, TestCaseReportArtifactDTO, TestCaseResultDTO


class XlsxTestCaseDiffFormatter(AbstractArtifactFormatter):
    artifact_type = "xlsx-testcase-diff"
    content_type = "application/vnd.opnexmlformats-officedocument.spreadsheetml.template"

    def format(self, result: TestResultDTO) -> TestCaseReportArtifactDTO:

        if not isinstance(result, TestCaseResultDTO):
            raise ValueError("xlsx formatting only supported for testcases not testruns")

        diff = result.diff["compare_sample_diff"]
        df = pl.DataFrame(diff)
        io = BytesIO()
        df.write_excel(io)

        raise NotImplementedError()
        return io.getbuffer().tobytes()
