from typing import Dict

from src.report.core.report import Report
from src.dtos import TestRunResultDTO, TestRunReportDTO, ReportArtifactDTO


class TestRunReport(Report):
    artifacts: Dict[str, ReportArtifactDTO]

    def __init__(self, result: TestRunResultDTO):
        super().__init__(result)
        self.result: TestRunResultDTO = result

    def to_dto(self) -> TestRunReportDTO:
        return TestRunReportDTO(
            testrun_id=self.result.testrun_id,
            start_ts=self.result.start_ts,
            end_ts=self.result.end_ts,
            result=self.result.result,
            artifacts=self.artifacts,
        )
