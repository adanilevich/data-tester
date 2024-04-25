from typing import Self
from src.dtos import TestRunResultDTO, TestRunReportDTO


class TestRunReport:

    @classmethod
    def from_testrun_result(cls, testrun_result: TestRunResultDTO) -> Self:
        """"""
        raise NotImplementedError()

    def as_dto(self) -> TestRunReportDTO:
        """"""
        raise NotImplementedError()
