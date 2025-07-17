from src.config import Config
from src.dtos import DomainConfigDTO, TestReportDTO, TestDTO, LocationDTO
from src.report.ports import (
    IReportCommandHandler,
    CreateReportCommand,
    SaveReportArtifactsForUsersCommand,
    SaveReportCommand,
)


# TODO remove configuration handling from here and put to dependency injection
# TODO: Add error handling here or in application if reports can't be formattted or saved
class CliReportManager:
    def __init__(
        self,
        report_handler: IReportCommandHandler,
        domain_config: DomainConfigDTO,
        config: Config,
    ):
        self.config = config
        self.report_handler = report_handler
        self.domain_config = domain_config

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

        testcase_report_format = self.config.TESTCASE_REPORT_ARTIFACT_FORMAT
        if testcase_report_format is None:
            raise ValueError("Testcase report artifact format is not set")

        testcase_diff_format = self.config.TESTCASE_DIFF_ARTIFACT_FORMAT
        if testcase_diff_format is None:
            raise ValueError("Testcase diff artifact format is not set")

        testrun_report_format = self.config.TESTRUN_REPORT_ARTIFACT_FORMAT
        if testrun_report_format is None:
            raise ValueError("Testrun report artifact format is not set")

        command = SaveReportArtifactsForUsersCommand(
            report=report,
            location=self.domain_config.testreports_location,
            testcase_report_format=testcase_report_format,
            testcase_diff_format=testcase_diff_format,
            testrun_report_format=testrun_report_format,
        )
        self.report_handler.save_report_artifacts_for_users(command=command)

    def save_report_in_internal_storage(self, report: TestReportDTO) -> None:
        """
        Saves all internal report artifacts to application-internal storage.
        """
        if self.config.INTERNAL_TESTREPORT_LOCATION is None:
            raise ValueError("Location for internal report artifacts is not set")
        location = LocationDTO(self.config.INTERNAL_TESTREPORT_LOCATION)

        artifact_format = self.config.INTERNAL_TESTREPORT_FORMAT
        if artifact_format is None:
            raise ValueError("Internal report artifact format is not set")

        command = SaveReportCommand(
            report=report,
            location=location,
            artifact_format=artifact_format,
        )
        self.report_handler.save_report(command=command)
