from typing import Dict
from src.report import Report
from src.dtos import TestCaseResultDTO, TestCaseReportDTO, ReportArtifactDTO


class TestCaseReport(Report):
    artifacts: Dict[str, ReportArtifactDTO]

    def __init__(self, result: TestCaseResultDTO):
        self.result: TestCaseResultDTO = result

    def to_dto(self) -> TestCaseReportDTO:
        """"""
        return TestCaseReportDTO(
            testrun_id=self.result.testrun_id,
            start_ts=self.result.start_ts,
            end_ts=self.result.end_ts,
            result=self.result.result,
            testcase_id=self.result.testcase_id,
            testobject=self.result.testobject,
            testcase=self.result.testtype,
            artifacts=self.artifacts,
        )
