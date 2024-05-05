from abc import ABC, abstractmethod
from typing import List

from src.dtos import DTO, TestCaseResultDTO, TestCaseReportDTO, ArtifactTag


class CreateTestCaseReportCommand(DTO):
    testcase_result: TestCaseResultDTO
    tags: List[ArtifactTag]


class ICreateTestCaseReportCommandHandler(ABC):
    @abstractmethod
    def create(self, command: CreateTestCaseReportCommand) -> TestCaseReportDTO:
        """Creates a testcase report in defined format"""
