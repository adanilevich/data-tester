from typing import List

from src.dtos import (
    TestRunReportDTO,
    TestCaseReportDTO,
    TestReportDTO,
)
from src.domain_ports import (
    IReportCommandHandler,
    CreateReportCommand,
    GetReportArtifactCommand,
    SaveReportCommand,
    LoadReportCommand,
)
from src.domain.report.plugins import IReportFormatter
from src.infrastructure_ports import IDtoStorage
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
        self,
        formatters: List[IReportFormatter],
        dto_storage: IDtoStorage,
    ):
        self.dto_storage = dto_storage
        self.report = Report(
            formatters=formatters, dto_storage=dto_storage
        )

    # TODO: split in create_testcase_report and create_testrun_report
    def create_report(
        self, command: CreateReportCommand
    ) -> TestReportDTO:
        """Creates a report from a test case result."""
        return self.report.create_report(command.result)

    def save_report(self, command: SaveReportCommand) -> None:
        """Saves report in application-internal storage."""

        if not isinstance(
            command.report, (TestRunReportDTO, TestCaseReportDTO)
        ):
            raise InvalidReportTypeError(
                f"Invalid report type: {type(command.report)}"
            )

        self.report.save_report(report=command.report)

    def load_report(self, command: LoadReportCommand) -> TestReportDTO:
        """Loads a report from internal storage."""
        return self.report.retrieve_report(
            report_id=str(command.report_id),
            report_type=command.report_type,
        )

    # TODO: split in create_testcase_report_artifact and create_testrun_report_artifact
    def get_report_artifact(self, command: GetReportArtifactCommand) -> bytes:
        """
        Retrieves a report by id from internal storage and
        creates requested artifact in requested format.
        """

        load_command = LoadReportCommand(
            report_id=command.report_id,
            report_type=command.report_type,
        )
        report_dto = self.load_report(load_command)

        formatted_artifact = self.report.create_artifact(
            report=report_dto,
            artifact=command.artifact,
            artifact_format=command.artifact_format,
        )

        return formatted_artifact

    # TODO: implement list_testcase_reports and list_testrun_reports. Note:
    # list_testrun_reports by domain and optionally by date
    # list_testcase_reports by domain and optionally by date and optionally by testrun_id
