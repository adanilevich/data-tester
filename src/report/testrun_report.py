from typing import Any, List, Self

from src.report import AbstractReport
from src.dtos import TestRunResultDTO, TestRunReportDTO, TestCaseResultDTO


class TestRunReport(AbstractReport):

    @classmethod
    def from_testrun_result(cls, testrun_result: TestRunResultDTO) -> Self:
        """"""
        return cls(
            testrun_id=testrun_result.testrun_id,
            start=testrun_result.start,
            end=testrun_result.end,
            result=testrun_result.result,
            testcase_results=testrun_result.testcase_results,
        )

    @classmethod
    def from_dto(cls, report_dto: TestRunReportDTO) -> Self:
        """"""
        return cls(
            testrun_id=report_dto.testrun_id,
            start=report_dto.start,
            end=report_dto.end,
            result=report_dto.result,
            testcase_results=report_dto.testcase_results,
            format=report_dto.format,
            content_type=report_dto.content_type,
            content=report_dto.content,
        )

    def __init__(self, testrun_id: str, start: str, end: str, result: str,
                 testcase_results: List[TestCaseResultDTO], format: str | None = None,
                 content_type: str | None = None, content: Any = None):

        self.testrun_id = testrun_id
        self.start = start
        self.end = end
        self.result = result
        self.testcase_results = testcase_results
        self.format = format
        self.content_type = content_type
        self.content = content

    def to_dto(self) -> TestRunReportDTO:
        """"""
        return TestRunReportDTO(
           testrun_id=self.testrun_id,
           start=self.start,
           end=self.end,
           result=self.result,
           testcase_results=self.testcase_results,
           format=self.format,
           content_type=self.content_type,
           content=self.content
        )
