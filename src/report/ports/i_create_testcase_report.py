from abc import ABC, abstractmethod

from src.dtos import DTO, TestCaseResultDTO, TestCaseReportDTO


class CreateTestCaseReportCommand(DTO):

    testcase_result: TestCaseResultDTO
    format: str


class ICreateTestCaseReportCommandHandler(ABC):

    @abstractmethod
    def create(self, command: CreateTestCaseReportCommand) -> TestCaseReportDTO:
        """Creates a testcase report in defined format"""
