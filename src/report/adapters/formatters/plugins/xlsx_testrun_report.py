from io import BytesIO

import polars as pl

from src.report.adapters.formatters import AbstractArtifactFormatter
from src.dtos import TestResultDTO, TestRunReportArtifactDTO, TestRunResultDTO


class XlsxTestRunReportFormatter(AbstractArtifactFormatter):

    artifact_type = "xlsx-testrun-report"
    content_type = "application/vnd.opnexmlformats-officedocument.spreadsheetml.template"

    def format(self, result: TestResultDTO) -> TestRunReportArtifactDTO:

        if not isinstance(result, TestRunResultDTO):
            raise ValueError("xlsx formatting only supported for testrun reports")

        results = [result.to_dict() for result in result.testcase_results]
        df = pl.DataFrame(results)
        io = BytesIO()
        df.write_excel(io)

        raise NotImplementedError()
        return io.getbuffer().tobytes()
