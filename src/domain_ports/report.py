from abc import ABC, abstractmethod

from pydantic import UUID4

from src.dtos.testcase import TestDTO
from src.dtos import (
    DTO,
    ReportType,
    TestReportDTO,
    ReportArtifact,
    ReportArtifactFormat,
)

#TODO: split in CreateTestCaseReportCommand and CreateTestRunReportCommand and then
# define the corresponding methonds
class CreateReportCommand(DTO):
    result: TestDTO

#TODO split in SaveTestCaseReport
class SaveReportCommand(DTO):
    report: TestReportDTO

#TODO: split in LoadTestCaseReportCommand and LoadTestRunReportCommand, then
# define corresponding methods
class LoadReportCommand(DTO):
    report_id: UUID4
    report_type: ReportType

#TODO: create ListTestCaseReportsCommand to list by domain and optionally testrun_id, date
#TODO: create ListTestRunReportsCommand to list by domain and optionally by date

class GetReportArtifactCommand(DTO):
    report_id: UUID4
    report_type: ReportType
    artifact: ReportArtifact
    artifact_format: ReportArtifactFormat


class IReportCommandHandler(ABC):
    @abstractmethod
    def create_report(
        self, command: CreateReportCommand
    ) -> TestReportDTO:
        """
        Creates a report for a given result.
        """

    @abstractmethod
    def save_report(self, command: SaveReportCommand) -> None:
        """
        Saves report in application-internal storage.
        """

    @abstractmethod
    def load_report(
        self, command: LoadReportCommand
    ) -> TestReportDTO:
        """
        Loads a report from internal storage.
        """

    @abstractmethod
    def get_report_artifact(
        self, command: GetReportArtifactCommand
    ) -> bytes:
        """
        Retrieves requested report from internal storage,
        creates requested artifact in requested format
        and returns as bytes.
        """
