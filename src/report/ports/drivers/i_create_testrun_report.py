from abc import ABC, abstractmethod
from typing import List
from src.dtos import DTO, TestRunReportDTO, TestRunResultDTO, ArtifactType


class CreateTestRunReportCommand(DTO):
    testrun_result: TestRunResultDTO
    artifact_types: List[ArtifactType]


class ICreateTestRunReportCommandHandler(ABC):
    @abstractmethod
    def create(self, command: CreateTestRunReportCommand) -> TestRunReportDTO:
        """Creates a testrun report in defined format"""
