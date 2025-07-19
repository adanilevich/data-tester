from typing import List

from src.report.application import ReportCommandHandler
from src.report.drivers import CliReportManager
from src.storage import map_storage, IStorage
from src.report.ports import IReportFormatter
from src.report.adapters import (
    XlsxTestCaseDiffFormatter,
    TxtTestCaseReportFormatter,
    JsonTestCaseReportFormatter,
    JsonTestRunReportFormatter,
    XlsxTestRunReportFormatter,
)
from src.config import Config
from src.dtos import DomainConfigDTO
from src.dtos.location import LocationDTO


class ReportDependencyInjector:
    def __init__(self, config: Config):
        self.config = config
        self.internal_storage: IStorage
        self.user_storage: IStorage
        self.storages: List[IStorage] = []

        self.internal_location: LocationDTO
        self.user_location: LocationDTO

        # set report formatters
        # if other user-facing report formats are implementd, change this code
        # to check application config which format is required
        self.user_testcase_report_formatter = TxtTestCaseReportFormatter()
        self.user_testcase_diff_formatter = XlsxTestCaseDiffFormatter()
        self.user_testrun_report_formatter = XlsxTestRunReportFormatter()
        self.internal_testrun_report_formatter = JsonTestRunReportFormatter()
        self.internal_testcase_report_formatter = JsonTestCaseReportFormatter()

        self.formatters: List[IReportFormatter] = [
            self.user_testcase_report_formatter,
            self.user_testcase_diff_formatter,
            self.user_testrun_report_formatter,
            self.internal_testrun_report_formatter,
            self.internal_testcase_report_formatter,
        ]

        # set internal storage
        self.internal_location = LocationDTO(
            self.config.DATATESTER_INTERNAL_TESTREPORT_LOCATION)
        self.internal_storage = map_storage(
            self.config.DATATESTER_INTERNAL_STORAGE_ENGINE)

        self.storages.append(self.internal_storage)

    def cli_report_manager(self, domain_config: DomainConfigDTO) -> CliReportManager:

        # set user report storage based on location in domain config
        self.user_location = domain_config.testreports_location
        self.user_storage = map_storage(self.user_location.store.value.upper())

        if type(self.user_storage) not in [type(s) for s in self.storages]:
            self.storages.append(self.user_storage)

        report_command_handler = ReportCommandHandler(
            storages=self.storages,
            formatters=self.formatters
        )
        return CliReportManager(
            report_handler=report_command_handler,
            user_location=self.user_location,
            internal_location=self.internal_location,
            internal_format = self.internal_testrun_report_formatter.artifact_format,
            user_report_format = self.user_testcase_report_formatter.artifact_format,
            user_diff_format = self.user_testcase_diff_formatter.artifact_format,
            user_testrun_format = self.user_testrun_report_formatter.artifact_format,
        )
