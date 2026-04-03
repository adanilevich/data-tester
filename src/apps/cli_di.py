from typing import List

from src.config import Config
from src.domain import (
    DomainConfigHandler,
    TestRunCommandHandler,
    IReportFormatter,
    ReportCommandHandler,
    TxtTestCaseReportFormatter,
    XlsxTestCaseDiffFormatter,
    XlsxTestRunReportFormatter,
    NamingConventionsFactory,
    SpecCommandHandler,
    FormatterFactory as SpecFormatterFactory,
    TestSetCommandHandler,
)
from src.drivers import (
    DomainConfigDriver,
    ReportDriver,
    SpecDriver,
    TestRunDriver,
    TestSetDriver,
)
from src.dtos import LocationDTO, StorageType
from src.infrastructure.backend import DemoBackendFactory, DummyBackendFactory
from src.infrastructure.notifier import InMemoryNotifier, StdoutNotifier
from src.infrastructure.storage import DtoStorageFactory, UserStorageFactory
from src.infrastructure_ports import INotifier, IDtoStorage, IBackendFactory, IUserStorage


def get_backend_factory(config: Config) -> IBackendFactory:
    platform_type = config.DATATESTER_DATA_PLATFORM
    if platform_type == "DEMO":
        return DemoBackendFactory()
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
        elif notifier == "STDOUT":
            notifiers.append(StdoutNotifier())
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
        self.spec_formatter_factory = SpecFormatterFactory()

    def domain_config_driver(self) -> DomainConfigDriver:
        handler = DomainConfigHandler(dto_storage=self.dto_storage)
        return DomainConfigDriver(domain_config_handler=handler)

    def testset_driver(self) -> TestSetDriver:
        handler = TestSetCommandHandler(dto_storage=self.dto_storage)
        return TestSetDriver(testset_handler=handler)

    def specification_driver(self) -> SpecDriver:
        handler = SpecCommandHandler(
            user_storage=self.user_storage,
            naming_conventions_factory=self.spec_naming_conventions_factory,
            formatter_factory=self.spec_formatter_factory,
        )
        return SpecDriver(spec_command_handler=handler)

    def testrun_driver(self) -> TestRunDriver:
        handler = TestRunCommandHandler(
            backend_factory=self.backend_factory,
            notifiers=self.notifiers,
            dto_storage=self.dto_storage,
        )
        return TestRunDriver(handler=handler)

    def report_driver(self) -> ReportDriver:
        handler = ReportCommandHandler(
            formatters=self.testreport_formatters,
            dto_storage=self.dto_storage,
        )
        return ReportDriver(report_handler=handler)
