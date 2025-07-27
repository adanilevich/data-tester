from src.dtos import ReportArtifactFormat, TestReportDTO, TestDTO, LocationDTO
from src.report.ports import (
    IReportCommandHandler,
    CreateReportCommand,
    SaveReportArtifactsForUsersCommand,
    SaveReportCommand,
)


class CliReportManager:
    def __init__(
        self,
        report_handler: IReportCommandHandler,
        user_location: LocationDTO,
        internal_location: LocationDTO,
        user_report_format: ReportArtifactFormat,
        user_diff_format: ReportArtifactFormat,
        user_testrun_format: ReportArtifactFormat,
    ):
        self.report_handler = report_handler
        self.user_location = user_location
        self.internal_location = internal_location
        self.user_report_format = user_report_format
        self.user_diff_format = user_diff_format
        self.user_testrun_format = user_testrun_format

    def create_report(self, result: TestDTO) -> TestReportDTO:
        """Creates testcase or testrun report"""

        command = CreateReportCommand(result=result)
        report = self.report_handler.create_report(command=command)

        return report

    def save_report_artifacts_for_users(self, report: TestReportDTO) -> None:
        """
        Saves user-facing report artifacts to user-managed storage locations.
        Several locations can be provided, e.g. storing in databases and in buckets or
        local storage.
        """

        command = SaveReportArtifactsForUsersCommand(
            report=report,
            location=self.user_location,
            testcase_report_format=self.user_report_format,
            testcase_diff_format=self.user_diff_format,
            testrun_report_format=self.user_testrun_format,
        )
        self.report_handler.save_report_artifacts_for_users(command=command)

    def save_report_in_internal_storage(self, report: TestReportDTO) -> None:
        """
        Saves all internal report artifacts to application-internal storage.
        """

        command = SaveReportCommand(
            report=report,
            location=self.internal_location,
        )
        self.report_handler.save_report(command=command)
