from abc import ABC, abstractmethod

from pydantic import UUID4

from src.dtos.testcase import TestDTO
from src.dtos import (
    DTO,
    LocationDTO,
    ReportType,
    TestReportDTO,
    ReportArtifact,
    ReportArtifactFormat,
)


class CreateReportCommand(DTO):
    result: TestDTO


class SaveReportCommand(DTO):
    report: TestReportDTO
    location: LocationDTO  # base location of internal report storage


class LoadReportCommand(DTO):
    report_id: UUID4
    location: LocationDTO  # base location of internal report storage
    report_type: ReportType  # look for testcase or testrun report


class GetReportArtifactCommand(DTO):
    report_id: UUID4
    report_type: ReportType  # look for testcase or testrun report
    location: LocationDTO  # base location of internal report storage
    artifact: ReportArtifact  # requested report artifact type, e.g. REPORT or DIFF
    artifact_format: ReportArtifactFormat  # requested report artifact format


class SaveReportArtifactsForUsersCommand(DTO):
    report: TestReportDTO
    location: LocationDTO  # base location of user-managed report storage
    testcase_report_format: ReportArtifactFormat  # user-managed tc report storage format
    testcase_diff_format: ReportArtifactFormat  # user-managed tc diff storage format
    testrun_report_format: ReportArtifactFormat  # user-managed tr report storage format


class IReportCommandHandler(ABC):
    @abstractmethod
    def create_report(self, command: CreateReportCommand) -> TestReportDTO:
        """
        Creates a report for a given result. Will return a TestRunReportDTO or a
        TestCaseReportDTO based on result type in the command.
        """

    @abstractmethod
    def save_report(self, command: SaveReportCommand) -> None:
        """
        Saves report in application-internal storage in internal format. Format musst
        be passed in the command by the driver.
        """

    @abstractmethod
    def load_report(self, command: LoadReportCommand) -> TestReportDTO:
        """
        Loads a report from internal storage.
        """

    @abstractmethod
    def get_report_artifact(self, command: GetReportArtifactCommand) -> bytes:
        """
        Retrieves requested report (testrun or testcase) from internal storage,
        creates requested artifact type (diff or report) in requested format
        and returns as bytes.
        """

    @abstractmethod
    def save_report_artifacts_for_users(
        self, command: SaveReportArtifactsForUsersCommand
    ) -> None:
        """
        Creates all possible report artifacts (diffs and reports) in requested formats
        (which are supposed to be usable by users, e.g. xlsx) and saves the artifacts
        in user-managed locations as specified in the command.
        """
