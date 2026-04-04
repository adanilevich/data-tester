from typing import List

from src.config import Config
from src.domain_adapters import (
    DomainConfigAdapter,
    TestRunAdapter,
    ReportAdapter,
    SpecAdapter,
    TestSetAdapter,
)
from src.domain.report.plugins import (
    IReportFormatter,
    TxtTestCaseReportFormatter,
    XlsxTestCaseDiffFormatter,
    XlsxTestRunReportFormatter,
)
from src.domain.specification import NamingConventionsFactory, SpecParserFactory
from src.drivers import (
    DomainConfigDriver,
    ReportDriver,
    SpecDriver,
    TestRunDriver,
    TestSetDriver,
)
from src.dtos import LocationDTO, StorageType
from src.infrastructure.backend import DemoBackendFactory, DummyBackendFactory
from src.infrastructure.notifier import InMemoryNotifier, LogNotifier
from src.infrastructure.storage import DtoStorageFactory, UserStorageFactory
from src.infrastructure_ports import INotifier, IDtoStorage, IBackendFactory, IUserStorage


def get_backend_factory(config: Config) -> IBackendFactory:
    platform_type = config.DATATESTER_DATA_PLATFORM
    if platform_type == "DEMO":
        return DemoBackendFactory(
            files_path=config.DATATESTER_DEMO_RAW_PATH,
            db_path=config.DATATESTER_DEMO_DB_PATH,
        )
    elif platform_type == "DUMMY":
        return DummyBackendFactory()
    else:
        raise ValueError(f"Unknown data platform type: {platform_type}")


def get_notifiers(config: Config) -> List[INotifier]:
    requested_notifiers = config.DATATESTER_NOTIFIERS
    notifiers: List[INotifier] = []
    for notifier in requested_notifiers:
        if notifier == "IN_MEMORY":
            notifiers.append(InMemoryNotifier())
        elif notifier == "LOG":
            notifiers.append(
                LogNotifier(
                    level=config.DATATESTER_LOG_LEVEL,
                    structured=True if config.DATATESTER_LOG_FORMAT == "JSON" else False,
                )
            )
        else:
            raise ValueError(f"Unknown notifier type: {notifier}")
    return notifiers


def get_dto_storage(config: Config) -> IDtoStorage:
    factory = DtoStorageFactory(gcp_project=config.DATATESTER_GCP_PROJECT)
    location = LocationDTO(config.DATATESTER_INTERNAL_STORAGE_LOCATION)
    storage = factory.get_storage(storage_location=location)
    return storage


def get_user_storage(config: Config) -> IUserStorage:
    factory = UserStorageFactory(gcp_project=config.DATATESTER_GCP_PROJECT)
    storage_type = StorageType(config.DATATESTER_USER_STORAGE_ENGINE.lower())
    storage = factory.get_storage(storage_type=storage_type)
    return storage


class CliDependencyInjector:
    def __init__(self, config: Config):
        self.config = config

        self.dto_storage: IDtoStorage = get_dto_storage(config)
        self.user_storage = get_user_storage(config)
        self.testreport_formatters: List[IReportFormatter] = [
            TxtTestCaseReportFormatter(),
            XlsxTestCaseDiffFormatter(),
            XlsxTestRunReportFormatter(),
        ]
        self.notifiers = get_notifiers(config)
        self.backend_factory = get_backend_factory(config)
        self.spec_naming_conventions_factory = NamingConventionsFactory()
        self.spec_formatter_factory = SpecParserFactory()

    def domain_config_driver(self) -> DomainConfigDriver:
        handler = DomainConfigAdapter(dto_storage=self.dto_storage)
        return DomainConfigDriver(domain_config_adapter=handler)

    def testset_driver(self) -> TestSetDriver:
        handler = TestSetAdapter(dto_storage=self.dto_storage)
        return TestSetDriver(testset_adapter=handler)

    def specification_driver(self) -> SpecDriver:
        handler = SpecAdapter(
            user_storage=self.user_storage,
            naming_conventions_factory=self.spec_naming_conventions_factory,
            formatter_factory=self.spec_formatter_factory,
            notifiers=self.notifiers,
        )
        return SpecDriver(spec_adapter=handler)

    def testrun_driver(self) -> TestRunDriver:
        handler = TestRunAdapter(
            backend_factory=self.backend_factory,
            notifiers=self.notifiers,
            dto_storage=self.dto_storage,
        )
        return TestRunDriver(testrun_adapter=handler)

    def report_driver(self) -> ReportDriver:
        handler = ReportAdapter(
            formatters=self.testreport_formatters,
            dto_storage=self.dto_storage,
            notifiers=self.notifiers,
        )
        return ReportDriver(report_adapter=handler)
