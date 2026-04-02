import pytest

from src.apps.cli_di import CliDependencyInjector, CommonDependencyInjector
from src.config import Config, ConfigError
from src.domain import (
    DomainConfigHandler,
    ReportCommandHandler,
    SpecCommandHandler,
    TestRunCommandHandler,
    TestSetCommandHandler,
    TxtTestCaseReportFormatter,
    XlsxTestCaseDiffFormatter,
    XlsxTestRunReportFormatter,
    FormatterFactory as SpecFormatterFactory,
    NamingConventionsFactory
)
from src.drivers import (
    DomainConfigDriver,
    ReportDriver,
    SpecDriver,
    TestRunDriver,
    TestSetDriver,
)
from src.dtos import (
    DomainConfigDTO,
    LocationDTO,
    TestCasesConfigDTO,
    SchemaTestCaseConfigDTO,
    CompareTestCaseConfigDTO,
    ReportArtifactFormat,
)
from src.infrastructure.backend import DemoBackendFactory, DummyBackendFactory
from src.infrastructure.notifier import InMemoryNotifier, StdoutNotifier
from src.infrastructure.storage import FormatterFactory, StorageFactory


def make_config(
    platform: str = "DUMMY",
    notifiers: list[str] | None = None,
    domain_configs_location: str = "dict://domain_configs/",
    testrun_location: str = "dict://testruns/",
    testreport_location: str = "dict://reports/",
    testset_location: str = "dict://testsets/",
) -> Config:
    config = Config()
    config.DATATESTER_DATA_PLATFORM = platform
    config.DATATESTER_NOTIFIERS = notifiers if notifiers is not None else ["IN_MEMORY"]
    config.DATATESTER_DOMAIN_CONFIGS_LOCATION = domain_configs_location
    config.DATATESTER_INTERNAL_TESTRUN_LOCATION = testrun_location
    config.DATATESTER_INTERNAL_TESTREPORT_LOCATION = testreport_location
    config.DATATESTER_INTERNAL_TESTSET_LOCATION = testset_location
    return config


@pytest.fixture
def config() -> Config:
    return make_config()


@pytest.fixture
def domain_config() -> DomainConfigDTO:
    return DomainConfigDTO(
        domain="test_domain",
        instances={"env": ["instance"]},
        specifications_locations=[LocationDTO("dict://specs/")],
        testreports_location=LocationDTO("dict://testreports/"),
        testcases=TestCasesConfigDTO(
            schema=SchemaTestCaseConfigDTO(compare_datatypes=["int"]),
            compare=CompareTestCaseConfigDTO(sample_size=10),
        ),
    )


# --- CommonDependencyInjector tests ---


class TestCommonDependencyInjector:
    def test_get_backend_returns_dummy(self, config: Config):
        # Given: data platform configured as DUMMY
        config.DATATESTER_DATA_PLATFORM = "DUMMY"
        di = CommonDependencyInjector(config)
        # When: requesting backend
        backend = di.get_backend()
        # Then: DummyBackendFactory is returned
        assert isinstance(backend, DummyBackendFactory)

    def test_get_backend_returns_demo(self, config: Config):
        # Given: data platform configured as DEMO
        config.DATATESTER_DATA_PLATFORM = "DEMO"
        di = CommonDependencyInjector(config)
        # When: requesting backend
        backend = di.get_backend()
        # Then: DemoBackendFactory is returned
        assert isinstance(backend, DemoBackendFactory)

    def test_get_backend_raises_on_unknown_platform(self, config: Config):
        # Given: unknown data platform type
        config.DATATESTER_DATA_PLATFORM = "UNKNOWN"
        di = CommonDependencyInjector(config)
        # When/Then: ValueError is raised
        with pytest.raises(ValueError, match="Unknown data platform type: UNKNOWN"):
            di.get_backend()

    def test_get_notifiers_returns_in_memory(self, config: Config):
        # Given: only IN_MEMORY notifier configured
        config.DATATESTER_NOTIFIERS = ["IN_MEMORY"]
        di = CommonDependencyInjector(config)
        # When: requesting notifiers
        notifiers = di.get_notifiers()
        # Then: one InMemoryNotifier is returned
        assert len(notifiers) == 1
        assert isinstance(notifiers[0], InMemoryNotifier)

    def test_get_notifiers_returns_stdout(self, config: Config):
        # Given: only STDOUT notifier configured
        config.DATATESTER_NOTIFIERS = ["STDOUT"]
        di = CommonDependencyInjector(config)
        # When: requesting notifiers
        notifiers = di.get_notifiers()
        # Then: one StdoutNotifier is returned
        assert len(notifiers) == 1
        assert isinstance(notifiers[0], StdoutNotifier)

    def test_get_notifiers_returns_multiple(self, config: Config):
        # Given: both notifiers configured
        config.DATATESTER_NOTIFIERS = ["IN_MEMORY", "STDOUT"]
        di = CommonDependencyInjector(config)
        # When: requesting notifiers
        notifiers = di.get_notifiers()
        # Then: both notifiers are returned in order
        assert len(notifiers) == 2
        assert isinstance(notifiers[0], InMemoryNotifier)
        assert isinstance(notifiers[1], StdoutNotifier)

    def test_get_notifiers_raises_on_unknown_notifier(self, config: Config):
        # Given: unknown notifier type
        config.DATATESTER_NOTIFIERS = ["UNKNOWN"]
        di = CommonDependencyInjector(config)
        # When/Then: ValueError is raised
        with pytest.raises(ValueError, match="Unknown notifier type: UNKNOWN"):
            di.get_notifiers()

    def test_get_notifiers_returns_empty_list(self, config: Config):
        # Given: no notifiers configured
        config.DATATESTER_NOTIFIERS = []
        di = CommonDependencyInjector(config)
        # When: requesting notifiers
        notifiers = di.get_notifiers()
        # Then: empty list returned
        assert notifiers == []


# --- CliDependencyInjector initialization tests ---


class TestCliDependencyInjectorInit:
    def test_raises_when_domain_configs_location_not_set(self):
        # Given: config without DATATESTER_DOMAIN_CONFIGS_LOCATION
        config = make_config()
        config.DATATESTER_DOMAIN_CONFIGS_LOCATION = None  # type: ignore
        # When/Then: ConfigError is raised
        with pytest.raises(
            ConfigError, match="DATATESTER_DOMAIN_CONFIGS_LOCATION is not set"
        ):
            CliDependencyInjector(config)

    def test_initializes_storage_factory(self, config: Config):
        # Given: valid config
        # When: creating injector
        injector = CliDependencyInjector(config)
        # Then: storage_factory is a StorageFactory with FormatterFactory
        assert isinstance(injector.storage_factory, StorageFactory)
        assert isinstance(injector.storage_factory.formatter_factory, FormatterFactory)

    def test_initializes_dc_storage_location(self, config: Config):
        # Given: domain configs location set to a specific path
        config.DATATESTER_DOMAIN_CONFIGS_LOCATION = "dict://my_configs/"
        # When: creating injector
        injector = CliDependencyInjector(config)
        # Then: dc_storage has the correct path
        assert isinstance(injector.dc_storage, LocationDTO)
        assert injector.dc_storage.path == "dict://my_configs/"

    def test_initializes_ts_storage_location(self, config: Config):
        # Given: testset location configured
        config.DATATESTER_INTERNAL_TESTSET_LOCATION = "dict://testsets/"
        # When: creating injector
        injector = CliDependencyInjector(config)
        # Then: ts_storage has the correct path
        assert isinstance(injector.ts_storage, LocationDTO)
        assert injector.ts_storage.path == "dict://testsets/"

    def test_initializes_testreport_storage_location(self, config: Config):
        # Given: testreport location configured
        config.DATATESTER_INTERNAL_TESTREPORT_LOCATION = "dict://reports/"
        # When: creating injector
        injector = CliDependencyInjector(config)
        # Then: testreport_storage has the correct path
        assert isinstance(injector.testreport_storage, LocationDTO)
        assert injector.testreport_storage.path == "dict://reports/"

    def test_initializes_testrun_storage_location(self, config: Config):
        # Given: testrun location configured
        config.DATATESTER_INTERNAL_TESTRUN_LOCATION = "dict://testruns/"
        # When: creating injector
        injector = CliDependencyInjector(config)
        # Then: testrun_storage has the correct path
        assert isinstance(injector.testrun_storage, LocationDTO)
        assert injector.testrun_storage.path == "dict://testruns/"

    def test_initializes_three_report_formatters(self, config: Config):
        # Given: valid config
        # When: creating injector
        injector = CliDependencyInjector(config)
        # Then: three formatters are created in the correct order
        assert len(injector.tr_formatters) == 3
        assert isinstance(injector.tr_formatters[0], TxtTestCaseReportFormatter)
        assert isinstance(injector.tr_formatters[1], XlsxTestCaseDiffFormatter)
        assert isinstance(injector.tr_formatters[2], XlsxTestRunReportFormatter)

    def test_initializes_notifiers(self, config: Config):
        # Given: IN_MEMORY notifier configured
        config.DATATESTER_NOTIFIERS = ["IN_MEMORY"]
        # When: creating injector
        injector = CliDependencyInjector(config)
        # Then: notifiers list contains one InMemoryNotifier
        assert len(injector.notifiers) == 1
        assert isinstance(injector.notifiers[0], InMemoryNotifier)

    def test_initializes_backend_factory_dummy(self, config: Config):
        # Given: DUMMY backend configured
        config.DATATESTER_DATA_PLATFORM = "DUMMY"
        # When: creating injector
        injector = CliDependencyInjector(config)
        # Then: backend_factory is DummyBackendFactory
        assert isinstance(injector.backend_factory, DummyBackendFactory)

    def test_initializes_backend_factory_demo(self, config: Config):
        # Given: DEMO backend configured
        config.DATATESTER_DATA_PLATFORM = "DEMO"
        # When: creating injector
        injector = CliDependencyInjector(config)
        # Then: backend_factory is DemoBackendFactory
        assert isinstance(injector.backend_factory, DemoBackendFactory)

    def test_initializes_spec_factories(self, config: Config):
        # Given: valid config
        # When: creating injector
        injector = CliDependencyInjector(config)
        # Then: spec naming conventions and formatter factories are created
        assert isinstance(
            injector.spec_naming_conventions_factory, NamingConventionsFactory
        )
        assert isinstance(injector.spec_formatter_factory, SpecFormatterFactory)


# --- CliDependencyInjector driver factory tests ---


class TestCliDependencyInjectorDrivers:
    def test_domain_config_driver_returns_correct_type(self, config: Config):
        # Given: valid injector
        injector = CliDependencyInjector(config)
        # When: creating domain config driver
        driver = injector.domain_config_driver()
        # Then: a DomainConfigDriver is returned
        assert isinstance(driver, DomainConfigDriver)

    def test_domain_config_driver_uses_shared_storage_factory(self, config: Config):
        # Given: valid injector
        injector = CliDependencyInjector(config)
        # When: creating domain config driver
        driver = injector.domain_config_driver()
        # Then: the handler uses the shared storage factory
        assert isinstance(driver.domain_config_handler, DomainConfigHandler)
        assert driver.domain_config_handler.storage_factory is injector.storage_factory

    def test_domain_config_driver_location(self, config: Config):
        # Given: specific domain config location
        config.DATATESTER_DOMAIN_CONFIGS_LOCATION = "dict://configs/"
        injector = CliDependencyInjector(config)
        # When: creating domain config driver
        driver = injector.domain_config_driver()
        # Then: driver has the correct location
        assert driver.domain_config_location.path == "dict://configs/"

    def test_testset_driver_returns_correct_type(self, config: Config):
        # Given: valid injector
        injector = CliDependencyInjector(config)
        # When: creating testset driver
        driver = injector.testset_driver()
        # Then: a TestSetDriver is returned
        assert isinstance(driver, TestSetDriver)

    def test_testset_driver_uses_shared_storage_factory(self, config: Config):
        # Given: valid injector
        injector = CliDependencyInjector(config)
        # When: creating testset driver
        driver = injector.testset_driver()
        # Then: the handler uses the shared storage factory
        assert isinstance(driver.testset_handler, TestSetCommandHandler)
        assert driver.testset_handler.storage_factory is injector.storage_factory

    def test_testset_driver_location(self, config: Config):
        # Given: specific testset location
        config.DATATESTER_INTERNAL_TESTSET_LOCATION = "dict://my_testsets/"
        injector = CliDependencyInjector(config)
        # When: creating testset driver
        driver = injector.testset_driver()
        # Then: driver has the correct location
        assert driver.storage_location.path == "dict://my_testsets/"

    def test_specification_driver_returns_correct_type(self, config: Config):
        # Given: valid injector
        injector = CliDependencyInjector(config)
        # When: creating specification driver
        driver = injector.specification_driver()
        # Then: a SpecDriver is returned
        assert isinstance(driver, SpecDriver)

    def test_specification_driver_uses_shared_storage_factory(self, config: Config):
        # Given: valid injector
        injector = CliDependencyInjector(config)
        # When: creating specification driver
        driver = injector.specification_driver()
        # Then: the handler uses the shared storage factory
        assert isinstance(driver.spec_command_handler, SpecCommandHandler)
        assert driver.spec_command_handler.storage_factory is injector.storage_factory

    def test_testrun_driver_returns_correct_type(self, config: Config):
        # Given: valid injector
        injector = CliDependencyInjector(config)
        # When: creating testrun driver
        driver = injector.testrun_driver()
        # Then: a TestRunDriver is returned
        assert isinstance(driver, TestRunDriver)

    def test_testrun_driver_location(self, config: Config):
        # Given: specific testrun location
        config.DATATESTER_INTERNAL_TESTRUN_LOCATION = "dict://my_testruns/"
        injector = CliDependencyInjector(config)
        # When: creating testrun driver
        driver = injector.testrun_driver()
        # Then: driver has the correct location
        assert driver.storage_location.path == "dict://my_testruns/"

    def test_testrun_driver_uses_configured_backend(self, config: Config):
        # Given: DEMO backend configured
        config.DATATESTER_DATA_PLATFORM = "DEMO"
        injector = CliDependencyInjector(config)
        # When: creating testrun driver
        driver = injector.testrun_driver()
        # Then: the handler uses the configured backend factory
        assert isinstance(driver.handler, TestRunCommandHandler)
        assert driver.handler.backend_factory is injector.backend_factory

    def test_testrun_driver_uses_configured_notifiers(self, config: Config):
        # Given: IN_MEMORY notifier configured
        config.DATATESTER_NOTIFIERS = ["IN_MEMORY"]
        injector = CliDependencyInjector(config)
        # When: creating testrun driver
        driver = injector.testrun_driver()
        # Then: the handler uses the configured notifiers
        assert isinstance(driver.handler, TestRunCommandHandler)
        assert driver.handler.notifiers is injector.notifiers

    def test_report_driver_returns_correct_type(
        self, config: Config, domain_config: DomainConfigDTO
    ):
        # Given: valid injector and domain config
        injector = CliDependencyInjector(config)
        # When: creating report driver
        driver = injector.report_driver(domain_config)
        # Then: a ReportDriver is returned
        assert isinstance(driver, ReportDriver)

    def test_report_driver_user_location(
        self, config: Config, domain_config: DomainConfigDTO
    ):
        # Given: domain config with specific testreports location
        injector = CliDependencyInjector(config)
        # When: creating report driver
        driver = injector.report_driver(domain_config)
        # Then: user_location matches domain config testreports_location
        assert driver.user_location.path == domain_config.testreports_location.path

    def test_report_driver_internal_location(
        self, config: Config, domain_config: DomainConfigDTO
    ):
        # Given: testreport storage configured at specific path
        config.DATATESTER_INTERNAL_TESTREPORT_LOCATION = "dict://int_reports/"
        injector = CliDependencyInjector(config)
        # When: creating report driver
        driver = injector.report_driver(domain_config)
        # Then: internal_location matches config
        assert driver.internal_location.path == "dict://int_reports/"

    def test_report_driver_formats(self, config: Config, domain_config: DomainConfigDTO):
        # Given: valid injector
        injector = CliDependencyInjector(config)
        # When: creating report driver
        driver = injector.report_driver(domain_config)
        # Then: report formats are set correctly
        assert driver.user_report_format == ReportArtifactFormat.TXT
        assert driver.user_diff_format == ReportArtifactFormat.XLSX
        assert driver.user_testrun_format == ReportArtifactFormat.XLSX

    def test_report_driver_uses_shared_storage_factory(
        self, config: Config, domain_config: DomainConfigDTO
    ):
        # Given: valid injector
        injector = CliDependencyInjector(config)
        # When: creating report driver
        driver = injector.report_driver(domain_config)
        # Then: handler uses the shared storage factory
        assert isinstance(driver.report_handler, ReportCommandHandler)
        assert driver.report_handler.storage_factory is injector.storage_factory
