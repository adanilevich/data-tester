from typing import Any, List, Self

from src.report.ports import IStorage, IReportFormatter, IReportNamingConventions
from src.report import AbstractReport
from src.dtos import TestRunResultDTO, TestRunReportDTO, TestCaseResultDTO


class TestRunReport(AbstractReport):

    @classmethod
    def from_testrun_result(
        cls,
        testrun_result: TestRunResultDTO,
        storage: IStorage,
        formatter: IReportFormatter,
        naming_conventions: IReportNamingConventions
    ) -> Self:
        """"""
        return cls(
            testrun_id=testrun_result.testrun_id,
            start_ts=testrun_result.start_ts,
            end_ts=testrun_result.end_ts,
            result=testrun_result.result,
            testcase_results=testrun_result.testcase_results,
            formatter=formatter,
            storage=storage,
            naming_conventions=naming_conventions,
        )

    @classmethod
    def from_dto(
        cls,
        report_dto: TestRunReportDTO,
        formatter: IReportFormatter,
        storage: IStorage,
        naming_conventions: IReportNamingConventions,
    ) -> Self:
        """"""
        return cls(
            testrun_id=report_dto.testrun_id,
            start_ts=report_dto.start_ts,
            end_ts=report_dto.end_ts,
            result=report_dto.result,
            testcase_results=report_dto.testcase_results,
            format=report_dto.format,
            content_type=report_dto.content_type,
            content=report_dto.content,
            formatter=formatter,
            storage=storage,
            naming_conventions=naming_conventions,
        )

    def __init__(self, formatter: IReportFormatter, storage: IStorage,
                 naming_conventions: IReportNamingConventions,
                 testrun_id: str, start_ts: str, end_ts: str, result: str,
                 testcase_results: List[TestCaseResultDTO], format: str | None = None,
                 content_type: str | None = None, content: Any = None):

        self.formatter: IReportFormatter = formatter
        self.storage: IStorage = storage
        self.naming_conventions: IReportNamingConventions = naming_conventions
        self.testrun_id: str = testrun_id
        self.start_ts: str = start_ts
        self.end_ts: str = end_ts
        self.result: str = result
        self.testcase_results: List[TestCaseResultDTO] = testcase_results
        self.format: str | None = format
        self.content_type: str | None = content_type
        self.content: Any = content

    def to_dto(self) -> TestRunReportDTO:
        """"""
        return TestRunReportDTO(
           testrun_id=self.testrun_id,
           start_ts=self.start_ts,
           end_ts=self.end_ts,
           result=self.result,
           testcase_results=self.testcase_results,
           format=self.format,
           content_type=self.content_type,
           content=self.content
        )
