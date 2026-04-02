from typing import List

from src.config import Config, ConfigError
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
    TestSetCommandHandler
)
from src.drivers import (
    DomainConfigDriver,
    ReportDriver,
    SpecDriver,
    TestRunDriver,
    TestSetDriver,
)
from src.dtos import DomainConfigDTO, LocationDTO
from src.infrastructure.backend import DemoBackendFactory, DummyBackendFactory
from src.infrastructure.notifier import InMemoryNotifier, StdoutNotifier
from src.infrastructure.storage import FormatterFactory, StorageFactory
from src.infrastructure_ports import INotifier


class CommonDependencyInjector:
    """Bundles dependency injection functions which are reused across apps"""

    def __init__(self, config: Config):
        self.config = config

    def get_backend(self) -> DemoBackendFactory | DummyBackendFactory:
        platform_type = self.config.DATATESTER_DATA_PLATFORM
        if platform_type == "DEMO":
            return DemoBackendFactory()
        elif platform_type == "DUMMY":
            return DummyBackendFactory()
        else:
            raise ValueError(f"Unknown data platform type: {platform_type}")

    def get_notifiers(self) -> List[INotifier]:
        requested_notifiers = self.config.DATATESTER_NOTIFIERS
        notifiers: List[INotifier] = []
        for notifier in requested_notifiers:
            if notifier == "IN_MEMORY":
                notifiers.append(InMemoryNotifier())
            elif notifier == "STDOUT":
                notifiers.append(StdoutNotifier())
            else:
                raise ValueError(f"Unknown notifier type: {notifier}")
        return notifiers


class CliDependencyInjector:
    def __init__(self, config: Config):
        self.config = config
        self.common_di = CommonDependencyInjector(config=self.config)

        # shared storage factory
        self.storage_factory = StorageFactory(FormatterFactory())

        # domain config
        if self.config.DATATESTER_DOMAIN_CONFIGS_LOCATION is None:
            raise ConfigError("DATATESTER_DOMAIN_CONFIGS_LOCATION is not set")
        self.dc_storage = LocationDTO(self.config.DATATESTER_DOMAIN_CONFIGS_LOCATION)

        # testset
        self.ts_storage = LocationDTO(self.config.DATATESTER_INTERNAL_TESTSET_LOCATION)

        # report
        self.testreport_storage = LocationDTO(
            self.config.DATATESTER_INTERNAL_TESTREPORT_LOCATION)
        self.user_testcase_report_formatter = TxtTestCaseReportFormatter()
        self.user_testcase_diff_formatter = XlsxTestCaseDiffFormatter()
        self.user_testrun_report_formatter = XlsxTestRunReportFormatter()
        self.tr_formatters: List[IReportFormatter] = [
            self.user_testcase_report_formatter,
            self.user_testcase_diff_formatter,
            self.user_testrun_report_formatter,
        ]

        # testrun
        self.notifiers = self.common_di.get_notifiers()
        self.backend_factory = self.common_di.get_backend()
        self.testrun_storage = LocationDTO(
            self.config.DATATESTER_INTERNAL_TESTRUN_LOCATION)

        # specification
        self.spec_naming_conventions_factory = NamingConventionsFactory()
        self.spec_formatter_factory = SpecFormatterFactory()

    def domain_config_driver(self) -> DomainConfigDriver:
        domain_config_handler = DomainConfigHandler(storage_factory=self.storage_factory)
        return DomainConfigDriver(
            domain_config_handler=domain_config_handler,
            domain_config_location=self.dc_storage,
        )

    def testset_driver(self) -> TestSetDriver:
        testset_handler = TestSetCommandHandler(storage_factory=self.storage_factory)
        return TestSetDriver(
            testset_handler=testset_handler,
            storage_location=self.ts_storage,
        )

    def specification_driver(self) -> SpecDriver:
        command_handler = SpecCommandHandler(
            storage_factory=self.storage_factory,
            naming_conventions_factory=self.spec_naming_conventions_factory,
            formatter_factory=self.spec_formatter_factory,
        )
        return SpecDriver(spec_command_handler=command_handler)

    def testrun_driver(self) -> TestRunDriver:
        return TestRunDriver(
            handler=TestRunCommandHandler(
                backend_factory=self.backend_factory,
                notifiers=self.notifiers,
                storage_factory=self.storage_factory,
            ),
            storage_location=self.testrun_storage,
        )

    def report_driver(self, domain_config: DomainConfigDTO) -> ReportDriver:
        report_command_handler = ReportCommandHandler(
            storage_factory=self.storage_factory,
            formatters=self.tr_formatters
        )
        return ReportDriver(
            report_handler=report_command_handler,
            user_location=domain_config.testreports_location,
            internal_location=self.testreport_storage,
            user_report_format=self.user_testcase_report_formatter.artifact_format,
            user_diff_format=self.user_testcase_diff_formatter.artifact_format,
            user_testrun_format=self.user_testrun_report_formatter.artifact_format,
        )
