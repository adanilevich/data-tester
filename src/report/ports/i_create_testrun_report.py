from abc import ABC, abstractmethod

from src.dtos import DTO, TestRunReportDTO, TestRunResultDTO


class CreateTestRunReportCommand(DTO):

    testrun_result: TestRunResultDTO
    format: str


class ICreateTestRunReportCommandHandler(ABC):

    @abstractmethod
    def create(self, command: CreateTestRunReportCommand) -> TestRunReportDTO:
        """Creates a testrun report in defined format"""
