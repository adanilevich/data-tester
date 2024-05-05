from src.report.adapters.formatters import AbstractArtifactFormatter
from src.dtos import TestResultDTO, TestCaseResultDTO, ReportArtifactDTO


class JsonTestCaseReportFormatter(AbstractArtifactFormatter):

    artifact_type = "json-testcase-report"
    content_type = "application/json"

    def format(self, result: TestResultDTO) -> ReportArtifactDTO:

        if not isinstance(result, TestCaseResultDTO):
            raise ValueError("Json formatting only supported for testcase reports")

        # TODO: implement this
        raise NotImplementedError()
