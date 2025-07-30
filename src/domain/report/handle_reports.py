from typing import List
from datetime import datetime

from pydantic import UUID4

from src.dtos import (
    TestRunReportDTO,
    TestCaseReportDTO,
    ReportArtifact,
    TestReportDTO,
    ReportArtifactFormat,
    LocationDTO,
)
from src.domain_ports import (
    IReportCommandHandler,
    CreateReportCommand,
    GetReportArtifactCommand,
    SaveReportArtifactsForUsersCommand,
    SaveReportCommand,
    LoadReportCommand,
)
from src.domain.report.plugins import IReportFormatter
from src.infrastructure_ports import IStorageFactory
from .report import Report


class InvalidReportTypeError(Exception):
    """Raised when an invalid report type is provided"""


class InvalidArtifactTypeError(Exception):
    """Raised when an invalid artifact type is provided"""


class ReportCommandHandler(IReportCommandHandler):
    """
    Handles the creation, storage and retrieval of reports.
    """

    def __init__(
        self, formatters: List[IReportFormatter], storage_factory: IStorageFactory
    ):
        self.formatters = formatters
        self.storage_factory = storage_factory
        self.report = Report(formatters=formatters, storage_factory=storage_factory)

    def create_report(self, command: CreateReportCommand) -> TestReportDTO:
        """
        Creates a report from a test case result provided by the command.
        """
        return self.report.create_report(command.result)

    def save_report(self, command: SaveReportCommand) -> None:
        """
        Saves report in application-internal storage in internal storage format as
        defined in the config.
        """

        if not isinstance(command.report, (TestRunReportDTO, TestCaseReportDTO)):
            raise InvalidReportTypeError(f"Invalid report type: {type(command.report)}")

        self.report.save_report(location=command.location, report=command.report)

    def load_report(self, command: LoadReportCommand) -> TestReportDTO:
        """
        Loads a report from internal storage.
        """
        reportDTO = self.report.retrieve_report(
            location=command.location,
            report_id=str(command.report_id),
            report_type=command.report_type,
        )

        return reportDTO

    def get_report_artifact(self, command: GetReportArtifactCommand) -> bytes:
        """
        Retrieves a report by id from application-internal storage and
        creates requested artifact type (report or diff) in requested format
        """

        load_command = LoadReportCommand(
            report_id=command.report_id,
            location=command.location,
            report_type=command.report_type,
        )
        reportDTO = self.load_report(load_command)

        formatted_artifact = self.report.create_artifact(
            report=reportDTO,
            artifact=command.artifact,
            artifact_format=command.artifact_format,
        )

        return formatted_artifact

    def save_report_artifacts_for_users(
        self, command: SaveReportArtifactsForUsersCommand
    ) -> None:
        """
        Saves report artifact in defined storage location. This method is for storing
        artifacts for users in user-managed storage locations (e.g. GCS buckets)
        """

        if isinstance(command.report, TestCaseReportDTO):
            artifact_location = self._testcase_artifact_location(
                location=command.location,
                report=command.report,
                artifact=ReportArtifact.REPORT,
                artifact_format=command.testcase_report_format,
            )
            artifact_bytes = self.report.create_artifact(
                report=command.report,
                artifact=ReportArtifact.REPORT,
                artifact_format=command.testcase_report_format,
            )
            self.report.save_artifact(artifact_location, artifact_bytes)

            # only generate and save a diff artifact if there is a diff
            if len(command.report.diff) > 0:
                artifact_location = self._testcase_artifact_location(
                    location=command.location,
                    report=command.report,
                    artifact=ReportArtifact.DIFF,
                    artifact_format=command.testcase_diff_format,
                )
                artifact_bytes = self.report.create_artifact(
                    report=command.report,
                    artifact=ReportArtifact.DIFF,
                    artifact_format=command.testcase_diff_format,
                )
                self.report.save_artifact(artifact_location, artifact_bytes)
        elif isinstance(command.report, TestRunReportDTO):
            artifact_location = self._testrun_artifact_location(
                location=command.location,
                report=command.report,
                artifact_format=command.testrun_report_format,
            )
            artifact_bytes = self.report.create_artifact(
                report=command.report,
                artifact=ReportArtifact.REPORT,
                artifact_format=command.testrun_report_format,
            )
            self.report.save_artifact(artifact_location, artifact_bytes)
        else:
            raise InvalidReportTypeError(f"Invalid report type: {type(command.report)}")

    @staticmethod
    def _testrun_artifact_location(
        location: LocationDTO,
        report: TestRunReportDTO,
        artifact_format: ReportArtifactFormat,
    ) -> LocationDTO:
        result = _user_report_location(location=location, testrun_id=report.testrun_id)
        result = result.append(
            "testrun_report_"
            + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            + "."
            + artifact_format.value.lower()
        )
        return result

    @staticmethod
    def _testcase_artifact_location(
        location: LocationDTO,
        report: TestCaseReportDTO,
        artifact: ReportArtifact,
        artifact_format: ReportArtifactFormat,
    ) -> LocationDTO:
        result = _user_report_location(location=location, testrun_id=report.testrun_id)
        result = result.append(
            report.testobject
            + "_"
            + report.testtype
            + "_"
            + artifact.value.lower()
            + "."
            + artifact_format.value.lower()
        )
        return result


def _user_report_location(location: LocationDTO, testrun_id: UUID4) -> LocationDTO:
    """
    Returns the location to be used for user-facing report artifacts
    Reports are saved in subfolders by date and testrun_id
    """
    result = location.append(datetime.now().strftime("%Y-%m-%d"))
    result = result.append(str(testrun_id))
    return result
