from typing import Self
from src.dtos import TestCaseResultDTO, TestCaseReportDTO


class TestCaseReport:

    @classmethod
    def from_testcase_result(cls, testcase_result: TestCaseResultDTO) -> Self:
        """"""
        raise NotImplementedError()

    def as_dto(self) -> TestCaseReportDTO:
        """"""
        raise NotImplementedError()
