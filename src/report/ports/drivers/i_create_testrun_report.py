from abc import ABC, abstractmethod
from typing import List

from src.dtos import DTO, TestRunReportDTO, TestRunResultDTO, ArtifactTag


class CreateTestRunReportCommand(DTO):
    testrun_result: TestRunResultDTO
    tags: List[ArtifactTag]


class ICreateTestRunReportCommandHandler(ABC):
    @abstractmethod
    def create(self, command: CreateTestRunReportCommand) -> TestRunReportDTO:
        """Creates a testrun report in defined format"""
