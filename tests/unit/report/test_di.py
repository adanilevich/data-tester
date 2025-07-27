import pytest

from src.config import Config
from src.dtos import (
    DomainConfigDTO,
    LocationDTO,
    TestCasesConfigDTO,
    SchemaTestCaseConfigDTO,
    CompareTestCaseConfigDTO,
)
from src.report.dependency_injection import ReportDependencyInjector
from src.report.drivers import CliReportManager
from src.storage import StorageFactory, FormatterFactory
from src.dtos.report import ReportArtifactFormat
from src.report.adapters.plugins import (
    TxtTestCaseReportFormatter,
    XlsxTestCaseDiffFormatter,
    XlsxTestRunReportFormatter,
)


@pytest.fixture
def config():
    """Create a test configuration"""
    return Config(
        DATATESTER_INTERNAL_STORAGE_ENGINE="DICT",
        DATATESTER_INTERNAL_TESTREPORT_LOCATION="dict://reports/",
    )


@pytest.fixture
def domain_config():
    """Create a test domain configuration"""
    return DomainConfigDTO(
        domain="test_domain",
        instances={"test": ["alpha"]},
        specifications_locations=[LocationDTO("dict://specs")],
        testreports_location=LocationDTO("dict://testreports"),
        testcases=TestCasesConfigDTO(
            schema=SchemaTestCaseConfigDTO(compare_datatypes=["int", "string"]),
            compare=CompareTestCaseConfigDTO(sample_size=100),
        ),
    )


class TestReportDependencyInjector:
    """Test suite for ReportDependencyInjector"""

    def test_initialization(self, config):
        """Test that ReportDependencyInjector initializes correctly with DICT storage"""
        # Given: a configuration with DICT storage engine
        # When: creating a ReportDependencyInjector
        injector = ReportDependencyInjector(config)

        # Then: the injector should be initialized with correct formatters and storage
        assert injector.config == config
        assert injector.internal_location.path == "dict://reports/"
        assert isinstance(injector.storage_factory, StorageFactory)
        assert injector.storage_factory.config == config
        assert isinstance(injector.storage_factory.formatter_factory, FormatterFactory)
        assert len(injector.formatters) == 3
        assert isinstance(injector.formatters[0], TxtTestCaseReportFormatter)
        assert isinstance(injector.formatters[1], XlsxTestCaseDiffFormatter)
        assert isinstance(injector.formatters[2], XlsxTestRunReportFormatter)

    def test_cli_report_manager_creation(self, config, domain_config):
        # Given: an application config and a report di and a domain config
        injector = ReportDependencyInjector(config)

        # When: creating a CLI report manager
        cli_manager = injector.cli_report_manager(domain_config)

        # Then: the CLI manager should be properly created
        assert isinstance(cli_manager, CliReportManager)
        assert cli_manager.user_location.path == "dict://testreports/"
        assert cli_manager.internal_location.path == "dict://reports/"
        assert cli_manager.user_report_format == ReportArtifactFormat.TXT
        assert cli_manager.user_diff_format == ReportArtifactFormat.XLSX
        assert cli_manager.user_testrun_format == ReportArtifactFormat.XLSX
