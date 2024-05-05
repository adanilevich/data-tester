from abc import ABC, abstractmethod
from typing import List
from src.dtos import DTO, TestCaseResultDTO, TestCaseReportDTO, ArtifactType


class CreateTestCaseReportCommand(DTO):
    testcase_result: TestCaseResultDTO
    artifact_types: List[ArtifactType]


class ICreateTestCaseReportCommandHandler(ABC):
    @abstractmethod
    def create(self, command: CreateTestCaseReportCommand) -> TestCaseReportDTO:
        """Creates a testcase report in defined format"""
