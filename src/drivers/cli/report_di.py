from typing import List

from src.domain.report import (
    ReportCommandHandler,
    IReportFormatter,
    XlsxTestCaseDiffFormatter,
    TxtTestCaseReportFormatter,
    XlsxTestRunReportFormatter,
)
from .report import CliReportManager
from src.infrastructure.storage import StorageFactory, FormatterFactory
from src.config import Config
from src.dtos import DomainConfigDTO
from src.dtos.location import LocationDTO


class ReportDependencyInjector:
    def __init__(self, config: Config):
        self.config = config
        self.storage_factory = StorageFactory(self.config, FormatterFactory())

        self.internal_location: LocationDTO
        self.user_location: LocationDTO  # to be set in cli_report_manager
        # since it depends on domain config

        # set report formatters
        # if other user-facing report formats are implementd, change this code
        # to check application config which format is required
        self.user_testcase_report_formatter = TxtTestCaseReportFormatter()
        self.user_testcase_diff_formatter = XlsxTestCaseDiffFormatter()
        self.user_testrun_report_formatter = XlsxTestRunReportFormatter()

        self.formatters: List[IReportFormatter] = [
            self.user_testcase_report_formatter,
            self.user_testcase_diff_formatter,
            self.user_testrun_report_formatter,
        ]

        # set internal storage location
        self.internal_location = LocationDTO(
            self.config.DATATESTER_INTERNAL_TESTREPORT_LOCATION
        )

    def cli_report_manager(self, domain_config: DomainConfigDTO) -> CliReportManager:
        # set user report location based on domain config
        self.user_location = domain_config.testreports_location

        report_command_handler = ReportCommandHandler(
            storage_factory=self.storage_factory, formatters=self.formatters
        )
        return CliReportManager(
            report_handler=report_command_handler,
            user_location=self.user_location,
            internal_location=self.internal_location,
            user_report_format=self.user_testcase_report_formatter.artifact_format,
            user_diff_format=self.user_testcase_diff_formatter.artifact_format,
            user_testrun_format=self.user_testrun_report_formatter.artifact_format,
        )
