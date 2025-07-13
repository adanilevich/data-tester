from typing import List

from src.config import Config
from src.dtos import DomainConfigDTO
from src.report.ports import (
    IReportCommandHandler,
    CreateReportCommand,
    SaveReportArtifactsForUsersCommand,
    SaveReportCommand,
)
from src.dtos import (
    TestCaseResultDTO,
    TestRunResultDTO,
    TestReportDTO,
    ReportType,
)


# TODO: Add error handling here or in application if reports can't be formattted or saved
class CliReportManager:
    def __init__(
        self,
        report_handler: IReportCommandHandler,
        domain_config: DomainConfigDTO,
        config: Config | None = None,
    ):
        self.config = config or Config()
        self.report_handler = report_handler
        self.domain_config = domain_config

    def create_report(self, type: ReportType, result: TestReportDTO) -> TestReportDTO:
        """Creates testcase report and populates report artifacts relevant for storage"""

        if type == ReportType.TESTCASE:
            if not isinstance(result, TestCaseResultDTO):
                raise ValueError("Result is not a TestCaseResultDTO")
        elif type == ReportType.TESTRUN:
            if not isinstance(result, TestRunResultDTO):
                raise ValueError("Result is not a TestRunResultDTO")
        else:
            raise ValueError("Invalid report type")

        command = CreateReportCommand(result=result)

        report = self.report_handler.create_report(command=command)

        return report

    def save_report_artifacts_for_users(
        self, report: TestReportDTO, locations: str | List[str] | None = None) -> None:
        """
        Saves user-facing report artifacts to user-managed storage locations.
        Several locations can be provided, e.g. storing in databases and in buckets or
        local storage.
        """

        locations = locations or self.domain_config.testreports_locations
        if locations is None:
            raise ValueError("Locations for user-facing report artifacts are not set")

        for location in locations:
            command = SaveReportArtifactsForUsersCommand(report=report, location=location)
            self.report_handler.save_report_artifacts_for_users(command=command)

    def save_report_in_internal_storage(
        self, report: TestReportDTO, location: str | None = None) -> None:
        """
        Saves all internal report artifacts to application-internal storage.
        """
        location = location or self.config.INTERNAL_TESTREPORT_LOCATION
        if location is None:
            raise ValueError("Location for internal report artifacts is not set")

        command = SaveReportCommand(report=report, location=location)
        self.report_handler.save_report(command=command)
