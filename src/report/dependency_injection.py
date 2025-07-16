from typing import List

from src.report.application import ReportCommandHandler
from src.report.drivers import CliReportManager
from src.report.ports import IStorage, IReportFormatter
from src.report.adapters import (
    XlsxTestCaseDiffFormatter,
    TxtTestCaseReportFormatter,
    JsonTestCaseReportFormatter,
    JsonTestRunReportFormatter,
    XlsxTestRunReportFormatter,
)
# from src.storage.file_storage import FileStorage
# from src.storage.dict_storage import DictStorage
from src.config import Config
from src.dtos import DomainConfigDTO, Store


class ReportDependencyInjector:
    def __init__(self, config: Config | None = None):
        self.config = config or Config()

    def report_manager(self, domain_config: DomainConfigDTO) -> CliReportManager:
        from src.storage.file_storage import FileStorage
        from src.storage.dict_storage import DictStorage
        storages: List[IStorage] = []

        # SET INTERNAL STORAGE BASED ON CONFIG
        internal_storage: IStorage
        if self.config.DATATESTER_ENV in ["DUMMY", "LOCAL"]:
            self.config.INTERNAL_STORAGE_ENGINE = "DICT"
        if self.config.INTERNAL_STORAGE_ENGINE == "DICT":
            internal_storage = DictStorage()
            self.config.INTERNAL_TESTREPORT_LOCATION = "dict://testreports"
        elif self.config.INTERNAL_STORAGE_ENGINE in ["LOCAL", "GCS", "MEMORY"]:
            internal_storage = FileStorage(config=self.config)
        else:
            msg = f"Unknown internal storage engine {self.config.INTERNAL_STORAGE_ENGINE}"
            raise ValueError(msg)
        storages.append(internal_storage)

        # SET USER REPORT STORAGE BASED ON DOMAIN CONFIG
        location = domain_config.testreports_location
        storage: IStorage
        if location.store in [Store.GCS, Store.LOCAL, Store.MEMORY]:
            storage = FileStorage(config=self.config)
        elif location.store == Store.DICT:
            storage = DictStorage()
        else:
            raise ValueError(f"Unknown user report location type {location}")
        if type(storage) not in [type(s) for s in storages]:
            storages.append(storage)

        # SET FORMATTERS BASED ON CONFIG
        formatters: List[IReportFormatter] = []
        if self.config.TESTCASE_REPORT_ARTIFACT_FORMAT.value.lower() == "txt":
            formatters.append(TxtTestCaseReportFormatter())
        if self.config.TESTCASE_DIFF_ARTIFACT_FORMAT.value.lower() == "xlsx":
            formatters.append(XlsxTestCaseDiffFormatter())
        if self.config.TESTRUN_REPORT_ARTIFACT_FORMAT.value.lower() == "xlsx":
            formatters.append(XlsxTestRunReportFormatter())
        if self.config.INTERNAL_TESTREPORT_FORMAT.value.lower() == "json":
            formatters.append(JsonTestRunReportFormatter())
            formatters.append(JsonTestCaseReportFormatter())

        report_command_handler = ReportCommandHandler(
            storages=storages,
            formatters=formatters
        )
        return CliReportManager(
            report_handler=report_command_handler,
            domain_config=domain_config,
            config=self.config
        )
