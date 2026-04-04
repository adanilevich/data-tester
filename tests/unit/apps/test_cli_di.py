import pytest

from src.apps.cli_di import CliDependencyInjector
from src.config import Config
from src.domain_adapters import (
    DomainConfigAdapter,
    ReportAdapter,
    SpecAdapter,
    TestRunAdapter,
)
from src.domain.report.plugins import (
    TxtTestCaseReportFormatter,
    XlsxTestCaseDiffFormatter,
    XlsxTestRunReportFormatter,
)
from src.domain.specification import SpecParserFactory, NamingConventionsFactory
from src.drivers import (
    DomainConfigDriver,
    ReportDriver,
    SpecDriver,
    TestRunDriver,
    TestSetDriver,
)
from src.infrastructure.backend import DemoBackendFactory, DummyBackendFactory
from src.infrastructure.notifier import InMemoryNotifier
from src.infrastructure_ports import IDtoStorage, IUserStorage


def make_config(
    platform: str = "DUMMY",
    notifiers: list[str] | None = None,
    storage_location: str = "memory://test/",
) -> Config:
    config = Config()
    config.DATATESTER_DATA_PLATFORM = platform
    config.DATATESTER_NOTIFIERS = notifiers if notifiers is not None else ["IN_MEMORY"]
    config.DATATESTER_INTERNAL_STORAGE_LOCATION = storage_location
    return config


@pytest.fixture
def config() -> Config:
    return make_config()


# --- CliDependencyInjector initialization tests ---


class TestCliDependencyInjectorInit:
    def test_initializes_dto_storage(self, config: Config):
        injector = CliDependencyInjector(config)
        assert isinstance(injector.dto_storage, IDtoStorage)

    def test_initializes_user_storage(self, config: Config):
        injector = CliDependencyInjector(config)
        assert isinstance(injector.user_storage, IUserStorage)

    def test_initializes_three_report_formatters(self, config: Config):
        injector = CliDependencyInjector(config)
        assert len(injector.testreport_formatters) == 3
        assert isinstance(injector.testreport_formatters[0], TxtTestCaseReportFormatter)
        assert isinstance(injector.testreport_formatters[1], XlsxTestCaseDiffFormatter)
        assert isinstance(injector.testreport_formatters[2], XlsxTestRunReportFormatter)

    def test_initializes_notifiers(self, config: Config):
        config.DATATESTER_NOTIFIERS = ["IN_MEMORY"]
        injector = CliDependencyInjector(config)
        assert len(injector.notifiers) == 1
        assert isinstance(injector.notifiers[0], InMemoryNotifier)

    def test_initializes_backend_factory_dummy(self, config: Config):
        config.DATATESTER_DATA_PLATFORM = "DUMMY"
        injector = CliDependencyInjector(config)
        assert isinstance(injector.backend_factory, DummyBackendFactory)

    def test_initializes_backend_factory_demo(self, config: Config):
        config.DATATESTER_DATA_PLATFORM = "DEMO"
        injector = CliDependencyInjector(config)
        assert isinstance(injector.backend_factory, DemoBackendFactory)

    def test_initializes_spec_factories(self, config: Config):
        injector = CliDependencyInjector(config)
        assert isinstance(
            injector.spec_naming_conventions_factory,
            NamingConventionsFactory,
        )
        assert isinstance(
            injector.spec_formatter_factory,
            SpecParserFactory,
        )


# --- CliDependencyInjector driver factory tests ---


class TestCliDependencyInjectorDrivers:
    def test_domain_config_driver_returns_correct_type(self, config: Config):
        injector = CliDependencyInjector(config)
        driver = injector.domain_config_driver()
        assert isinstance(driver, DomainConfigDriver)

    def test_domain_config_driver_handler_uses_shared_dto_storage(self, config: Config):
        injector = CliDependencyInjector(config)
        driver = injector.domain_config_driver()
        assert isinstance(
            driver.adapter,
            DomainConfigAdapter,
        )
        assert driver.adapter.dto_storage is injector.dto_storage

    def test_testset_driver_returns_correct_type(self, config: Config):
        injector = CliDependencyInjector(config)
        driver = injector.testset_driver()
        assert isinstance(driver, TestSetDriver)

    def test_specification_driver_returns_correct_type(self, config: Config):
        injector = CliDependencyInjector(config)
        driver = injector.specification_driver()
        assert isinstance(driver, SpecDriver)

    def test_specification_driver_uses_user_storage(self, config: Config):
        injector = CliDependencyInjector(config)
        driver = injector.specification_driver()
        assert isinstance(
            driver.adapter,
            SpecAdapter,
        )
        assert driver.adapter.user_storage is injector.user_storage

    def test_testrun_driver_returns_correct_type(self, config: Config):
        injector = CliDependencyInjector(config)
        driver = injector.testrun_driver()
        assert isinstance(driver, TestRunDriver)

    def test_testrun_driver_uses_configured_backend(self, config: Config):
        config.DATATESTER_DATA_PLATFORM = "DEMO"
        injector = CliDependencyInjector(config)
        driver = injector.testrun_driver()
        assert isinstance(driver.adapter, TestRunAdapter)
        assert driver.adapter.backend_factory is injector.backend_factory

    def test_testrun_driver_uses_configured_notifiers(self, config: Config):
        config.DATATESTER_NOTIFIERS = ["IN_MEMORY"]
        injector = CliDependencyInjector(config)
        driver = injector.testrun_driver()
        assert isinstance(driver.adapter, TestRunAdapter)
        assert driver.adapter.notifiers is injector.notifiers

    def test_testrun_driver_uses_shared_dto_storage(self, config: Config):
        injector = CliDependencyInjector(config)
        driver = injector.testrun_driver()
        assert isinstance(driver.adapter, TestRunAdapter)
        assert driver.adapter.dto_storage is injector.dto_storage

    def test_report_driver_returns_correct_type(self, config: Config):
        injector = CliDependencyInjector(config)
        driver = injector.report_driver()
        assert isinstance(driver, ReportDriver)

    def test_report_driver_uses_shared_dto_storage(self, config: Config):
        injector = CliDependencyInjector(config)
        driver = injector.report_driver()
        assert isinstance(driver.adapter, ReportAdapter)
        assert driver.adapter.dto_storage is injector.dto_storage
