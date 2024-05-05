from src.report.plugins import IReportArtifact
from src.dtos import TestResultDTO, TestCaseResultDTO, ReportArtifactDTO


class JsonTestCaseReportFormatter(IReportArtifact):

    artifact_type = "json-testcase-report"
    content_type = "application/json"

    def format(self, result: TestResultDTO) -> ReportArtifactDTO:

        if not isinstance(result, TestCaseResultDTO):
            raise ValueError("Json formatting only supported for testcase reports")

        # TODO: implement this
        raise NotImplementedError()
