from typing import Any, List, Self

from src.report import AbstractReport
from src.dtos import TestRunResultDTO, TestRunReportDTO, TestCaseResultDTO


class TestRunReport(AbstractReport):
    def __init__(
        self,
        testrun_id: str,
        start_ts: str,
        end_ts: str,
        result: str,
        testcase_results: List[TestCaseResultDTO],
        report_format: str | None = None,
        content_type: str | None = None,
        content: Any = None,
    ):
        self.testrun_id: str = testrun_id
        self.start_ts: str = start_ts
        self.end_ts: str = end_ts
        self.result: str = result
        self.testcase_results: List[TestCaseResultDTO] = testcase_results
        self.report_format: str | None = report_format
        self.content_type: str | None = content_type
        self.content: Any = content

    def to_dto(self) -> TestRunReportDTO:
        return TestRunReportDTO(
            testrun_id=self.testrun_id,
            start_ts=self.start_ts,
            end_ts=self.end_ts,
            result=self.result,
            testcase_results=self.testcase_results,
            report_format=self.report_format,
            content_type=self.content_type,
            content=self.content,
        )

    @classmethod
    def from_testrun_result(cls, testrun_result: TestRunResultDTO) -> Self:
        return cls(
            testrun_id=testrun_result.testrun_id,
            start_ts=testrun_result.start_ts,
            end_ts=testrun_result.end_ts,
            result=testrun_result.result,
            testcase_results=testrun_result.testcase_results,
        )

    @classmethod
    def from_dto(cls, report_dto: TestRunReportDTO) -> Self:
        return cls(
            testrun_id=report_dto.testrun_id,
            start_ts=report_dto.start_ts,
            end_ts=report_dto.end_ts,
            result=report_dto.result,
            testcase_results=report_dto.testcase_results,
            report_format=report_dto.report_format,
            content_type=report_dto.content_type,
            content=report_dto.content,
        )
