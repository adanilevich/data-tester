from typing import List
from datetime import datetime

from src.dtos.report import (
    TestRunReportDTO,
    TestCaseReportDTO,
    ReportArtifact,
    TestReportDTO,
    ReportArtifactFormat,
)
from src.report.ports.drivers import (
    IReportCommandHandler,
    CreateReportCommand,
    GetTestCaseReportArtifactCommand,
    GetTestrunReportArtifactCommand,
    SaveReportArtifactsForUsersCommand,
    SaveReportCommand,
)
from src.report.core import Report
from src.report.ports.plugins import IReportFormatter
from src.report.ports.infrastructure import IStorage
from src.config import Config


class InvalidReportTypeError(Exception):
    """Raised when an invalid report type is provided"""


class InvalidArtifactTypeError(Exception):
    """Raised when an invalid artifact type is provided"""


# TODO: Add error handling here or in drivers if reports can't be formattted or saved
class ReportCommandHandler(IReportCommandHandler):
    """
    Handles the creation, storage and retrieval of reports.
    """

    def __init__(
        self, config: Config, formatters: List[IReportFormatter], storages: List[IStorage]
    ):
        self.config = config
        self.formatters = formatters
        self.storages = storages
        self.report = Report(formatters=formatters, storages=storages)

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

        location = self._get_internal_report_location_by_report(
            report=command.report, location=command.location
        )

        report_bytes = self.report.create_artifact(
            report=command.report,
            artifact=ReportArtifact.REPORT,
            artifact_format=self.config.INTERNAL_TESTREPORT_FORMAT,
        )
        self.report.save_artifact(location=location, artifact=report_bytes)

    def get_testcase_report_artifact(
        self, command: GetTestCaseReportArtifactCommand) -> bytes:
        """
        Retrieves a report by id from application-internal storage and
        creates requested artifact type (report or diff) in requested format
        """
        location = self._get_internal_report_location_by_ids(
            testrun_id=command.testrun_id,
            testcase_id=command.testcase_id,
            location=command.location,
        )
        reportDTO = self.report.retrieve_report(location=location)

        if not isinstance(reportDTO, TestCaseReportDTO):
            raise InvalidReportTypeError("Can't create testcase artifacts from testrun")

        artifact_format = self._get_artifact_format(command.artifact, type(reportDTO))

        formatted_artifact = self.report.create_artifact(
            report=reportDTO, artifact=command.artifact, artifact_format=artifact_format
        )

        return formatted_artifact

    def get_testrun_report_artifact(
        self, command: GetTestrunReportArtifactCommand) -> bytes:
        """
        Retrieves a report by id from application-internal storage and
        creates testrun report in requested format
        """

        location = self._get_internal_report_location_by_ids(
            testrun_id=command.testrun_id, location=command.location
        )

        reportDTO = self.report.retrieve_report(location=location)

        if not isinstance(reportDTO, TestRunReportDTO):
            raise InvalidReportTypeError("Can't create testrun artifacts from testcase")

        formatted_artifact = self.report.create_artifact(
            report=reportDTO,
            artifact_format=self.config.TESTRUN_REPORT_ARTIFACT_FORMAT,
            artifact=ReportArtifact.REPORT,
        )

        return formatted_artifact

    def save_report_artifacts_for_users(
        self, command: SaveReportArtifactsForUsersCommand) -> None:
        """
        Saves report artifact in defined storage location. This method is for storing
        artifacts for users in user-managed storage locations (e.g. GCS buckets)
        """

        location = self._get_user_report_location(command)
        format_ = self._get_artifact_format(ReportArtifact.REPORT, type(command.report))

        artifact_bytes = self.report.create_artifact(
            report=command.report,
            artifact=ReportArtifact.REPORT,
            artifact_format=format_,
        )

        filename = self._get_artifact_filename(command.report, ReportArtifact.REPORT)
        self.report.save_artifact(location + filename, artifact_bytes)

        # only generate and save a diff artifact if there is a diff
        if isinstance(command.report, TestCaseReportDTO) and len(command.report.diff) > 0:
            artifact_bytes = self.report.create_artifact(
                report=command.report,
                artifact=ReportArtifact.DIFF,
                artifact_format=self.config.TESTCASE_DIFF_ARTIFACT_FORMAT,
            )

            filename = self._get_artifact_filename(command.report, ReportArtifact.DIFF)
            self.report.save_artifact(location + filename, artifact_bytes)

    def _get_artifact_filename(
        self, report: TestReportDTO, artifact: ReportArtifact
    ) -> str:
        """Returns the filename under which the artifact is to be stored"""

        datetime_str = report.start_ts.strftime("%Y-%m-%d_%H-%M-%S")

        if isinstance(report, TestRunReportDTO):
            artifact_format = self.config.TESTRUN_REPORT_ARTIFACT_FORMAT
            filename = (
                "testrun_report_"
                + datetime_str
                + "."
                + artifact_format.value.lower()
            )
        elif isinstance(report, TestCaseReportDTO):
            if artifact == ReportArtifact.REPORT:
                artifact_format = self.config.TESTCASE_REPORT_ARTIFACT_FORMAT
                suffix = "report"
            elif artifact == ReportArtifact.DIFF:
                artifact_format = self.config.TESTCASE_DIFF_ARTIFACT_FORMAT
                suffix = "diff"
            else:
                raise InvalidArtifactTypeError(f"Invalid artifact type: {artifact}")

            filename = (
                report.testobject
                + "_"
                + report.testtype
                + "_"
                + suffix
                + "."
                + artifact_format.value.lower()
            )
        else:
            raise InvalidReportTypeError(f"Invalid report type: {type(report)}")

        return filename

    def _get_artifact_format(
        self, artifact: ReportArtifact, type: type[TestReportDTO]
    ) -> ReportArtifactFormat:
        """Returns the artifact format for the report"""

        if type == TestRunReportDTO:
            return self.config.TESTRUN_REPORT_ARTIFACT_FORMAT
        elif type == TestCaseReportDTO:
            if artifact == ReportArtifact.REPORT:
                return self.config.TESTCASE_REPORT_ARTIFACT_FORMAT
            elif artifact == ReportArtifact.DIFF:
                return self.config.TESTCASE_DIFF_ARTIFACT_FORMAT
            else:
                raise InvalidArtifactTypeError(f"Invalid artifact type: {artifact}")
        else:
            raise InvalidReportTypeError(f"Invalid report type: {type}")

    @staticmethod
    def _get_user_report_location(command: SaveReportArtifactsForUsersCommand) -> str:
        """
        Returns the location to be used for user-facing report artifacts
        Reports are saved in subfolders by date and testrun_id
        """
        location = command.location
        location += "/" if not location.endswith("/") else location
        location += datetime.now().strftime("%Y-%m-%d") + "/"
        location += str(command.report.testrun_id) + "/"

        return location

    def _get_internal_report_location_by_report(
        self, report: TestReportDTO, location: str
    ) -> str:
        testrun_id = str(report.testrun_id)

        if not isinstance(report, (TestRunReportDTO, TestCaseReportDTO)):
            raise InvalidReportTypeError(f"Invalid report type: {type(report)}")

        new_location = location
        if not new_location.endswith("/"):
            new_location += "/"

        artifact_format = self.config.INTERNAL_TESTREPORT_FORMAT

        if isinstance(report, TestCaseReportDTO):
            testcase_id = str(report.testcase_id)
            new_location += (
                "testcase_reports/"
                + str(testrun_id)
                + "_"
                + str(testcase_id)
                + "." + artifact_format.value.lower()
            )
        elif isinstance(report, TestRunReportDTO):
            new_location += (
                "testrun_reports/" + str(testrun_id) + "." + artifact_format.value.lower()
            )

        return new_location

    def _get_internal_report_location_by_ids(
        self, testrun_id: str, location: str, testcase_id: str | None = None
    ) -> str:
        new_location = location
        if not new_location.endswith("/"):
            new_location += "/"

        if testcase_id is not None:
            new_location += (
                "testcase_reports/"
                + str(testrun_id)
                + "_"
                + str(testcase_id)
                + "." + self.config.INTERNAL_TESTREPORT_FORMAT.value.lower()
            )
        else:
            new_location += (
                "testrun_reports/"
                + str(testrun_id)
                + "."
                + self.config.INTERNAL_TESTREPORT_FORMAT.value.lower()
            )
        return new_location
