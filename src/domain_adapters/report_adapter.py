from typing import List

from src.dtos import (
    TestRunReportDTO,
    TestCaseReportDTO,
)
from src.domain_ports import (
    IReport,
    CreateTestCaseReportCommand,
    CreateTestRunReportCommand,
    CreateTestCaseReportArtifactCommand,
    CreateTestRunReportArtifactCommand,
    CreateAndSaveAllReportsCommand,
    SaveReportCommand,
    LoadTestCaseReportCommand,
    LoadTestRunReportCommand,
    ListTestCaseReportsCommand,
    ListTestRunReportsCommand,
)
from src.domain.report.plugins import IReportFormatter
from src.infrastructure_ports import IDtoStorage
from src.domain.report.report import Report


class InvalidReportTypeError(Exception):
    """Raised when an invalid report type is provided."""


class ReportAdapter(IReport):
    """Handles the creation, storage and retrieval of reports."""

    def __init__(
        self,
        formatters: List[IReportFormatter],
        dto_storage: IDtoStorage,
    ):
        self.dto_storage = dto_storage
        self.report = Report(formatters=formatters, dto_storage=dto_storage)

    def create_testcase_report(
        self, command: CreateTestCaseReportCommand
    ) -> TestCaseReportDTO:
        """Creates a report from a testcase result."""
        return self.report.create_testcase_report(command.result)

    def create_testrun_report(
        self, command: CreateTestRunReportCommand
    ) -> TestRunReportDTO:
        """Creates a report from a testrun result."""
        return self.report.create_testrun_report(command.result)

    def save_report(self, command: SaveReportCommand) -> None:
        """Saves report in application-internal storage."""
        if not isinstance(command.report, (TestRunReportDTO, TestCaseReportDTO)):
            raise InvalidReportTypeError(f"Invalid report type: {type(command.report)}")
        self.report.save_report(report=command.report)

    def load_testcase_report(
        self, command: LoadTestCaseReportCommand
    ) -> TestCaseReportDTO:
        """Loads a testcase report from internal storage."""
        return self.report.load_testcase_report(report_id=str(command.report_id))

    def load_testrun_report(self, command: LoadTestRunReportCommand) -> TestRunReportDTO:
        """Loads a testrun report from internal storage."""
        return self.report.load_testrun_report(report_id=str(command.report_id))

    def list_testcase_reports(
        self, command: ListTestCaseReportsCommand
    ) -> List[TestCaseReportDTO]:
        """Lists testcase reports by domain."""
        return self.report.list_testcase_reports(
            domain=command.domain,
            testrun_id=str(command.testrun_id) if command.testrun_id else None,
            date=command.date,
        )

    def list_testrun_reports(
        self, command: ListTestRunReportsCommand
    ) -> List[TestRunReportDTO]:
        """Lists testrun reports by domain."""
        return self.report.list_testrun_reports(domain=command.domain, date=command.date)

    def create_testcase_report_artifact(
        self, command: CreateTestCaseReportArtifactCommand
    ) -> bytes:
        """Loads a testcase report and creates the requested artifact."""
        report_dto = self.report.load_testcase_report(report_id=str(command.report_id))
        return self.report.create_testcase_report_artifact(
            report=report_dto,
            artifact=command.artifact,
            artifact_format=command.artifact_format,
        )

    def create_testrun_report_artifact(
        self, command: CreateTestRunReportArtifactCommand
    ) -> bytes:
        """Loads a testrun report and creates the requested artifact."""
        report_dto = self.report.load_testrun_report(report_id=str(command.report_id))
        return self.report.create_testrun_report_artifact(
            report=report_dto,
            artifact_format=command.artifact_format,
        )

    def create_and_save_all_reports(
        self, command: CreateAndSaveAllReportsCommand
    ) -> TestRunReportDTO:
        """Creates and saves all reports for a testrun and its testcases."""
        return self.report.create_and_save_all_reports(command.testrun)
