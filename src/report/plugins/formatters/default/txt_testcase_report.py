import yaml  # type: ignore
from src.report.plugins import IReportArtifact
from src.dtos import TestResultDTO, TestCaseResultDTO, ReportArtifactDTO


class TxtTestCaseReportFormatter(IReportArtifact):

    artifact_type = "txt-testcase-report"
    content_type = "text/plain"

    def format(self, result: TestResultDTO) -> ReportArtifactDTO:
        if not isinstance(result, TestCaseResultDTO):
            raise ValueError("txt formatting only supported for testcase reports.")

        return yaml.safe_dump(data=result.to_dict(), default_flow_style=None, indent=4)
