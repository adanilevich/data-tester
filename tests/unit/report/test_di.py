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
from src.storage import DictStorage, FileStorage
from src.dtos.report import ReportArtifactFormat


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

    def test_initialization_with_dict_storage(self, config):
        """Test that ReportDependencyInjector initializes correctly with DICT storage"""
        # Given: a configuration with DICT storage engine
        # When: creating a ReportDependencyInjector
        injector = ReportDependencyInjector(config)

        # Then: the injector should be initialized with correct formatters and storage
        assert isinstance(injector.config, Config)
        assert isinstance(injector.internal_storage, DictStorage)
        assert len(injector.storages) == 1
        assert isinstance(injector.storages[0], DictStorage)
        assert injector.internal_location.path == "dict://reports/"

    def test_initialization_with_file_storage(self):
        """Test that ReportDependencyInjector initializes correctly with LOCAL storage"""
        # Given: a configuration with LOCAL storage engine
        config = Config(
            DATATESTER_ENV="PROD",  # Override LOCAL mode to prevent auto-override
            DATATESTER_INTERNAL_STORAGE_ENGINE="LOCAL",
            DATATESTER_INTERNAL_TESTREPORT_LOCATION="local://reports/",
        )

        # When: creating a ReportDependencyInjector
        injector = ReportDependencyInjector(config)

        # Then: the injector should use FileStorage for internal storage
        assert isinstance(injector.internal_storage, FileStorage)
        assert len(injector.storages) == 1
        assert isinstance(injector.storages[0], FileStorage)
        assert injector.internal_location.path == "local://reports/"

    def test_cli_report_manager_creation_with_dict_storage(self, config, domain_config):
        """Test CLI report manager creation with DICT storage"""
        # Given: a configuration and domain config with DICT storage
        injector = ReportDependencyInjector(config)

        # When: creating a CLI report manager
        cli_manager = injector.cli_report_manager(domain_config)

        # Then: the CLI manager should be properly created
        assert isinstance(cli_manager, CliReportManager)
        assert cli_manager.user_location.path == "dict://testreports/"
        assert cli_manager.internal_location.path == "dict://reports/"
        assert cli_manager.internal_format == ReportArtifactFormat.JSON
        assert cli_manager.user_report_format == ReportArtifactFormat.TXT
        assert cli_manager.user_diff_format == ReportArtifactFormat.XLSX
        assert cli_manager.user_testrun_format == ReportArtifactFormat.XLSX

    def test_cli_report_manager_creation_with_file_storage(self, domain_config):
        """Test CLI report manager creation with LOCAL storage"""
        # Given: a configuration with LOCAL storage and domain config with DICT storage
        config = Config(
            DATATESTER_ENV="PROD",  # Override LOCAL mode to prevent auto-override
            DATATESTER_INTERNAL_STORAGE_ENGINE="LOCAL",
            DATATESTER_INTERNAL_TESTREPORT_LOCATION="local://reports/",
        )
        injector = ReportDependencyInjector(config)

        # When: creating a CLI report manager
        cli_manager = injector.cli_report_manager(domain_config)

        # Then: the CLI manager should be properly created with correct storage types
        assert isinstance(cli_manager, CliReportManager)
        assert len(injector.storages) == 2  # internal + user storage
        assert any(isinstance(storage, FileStorage) for storage in injector.storages)
        assert any(isinstance(storage, DictStorage) for storage in injector.storages)

    def test_invalid_storage_engine_raises_error(self):
        """Test that invalid storage engine raises ValueError"""
        # Given: a configuration with invalid storage engine
        config = Config(
            DATATESTER_ENV="PROD",  # Override LOCAL mode to prevent auto-override
            DATATESTER_INTERNAL_STORAGE_ENGINE="INVALID_ENGINE",
            DATATESTER_INTERNAL_TESTREPORT_LOCATION="dict://reports/",
        )

        # When/Then: creating a ReportDependencyInjector should raise ValueError
        with pytest.raises(ValueError, match="Unknown storage engine: INVALID_ENGINE"):
            ReportDependencyInjector(config)

    def test_location_initialization(self, config):
        """Test that locations are properly initialized"""
        # Given: a configuration with specific location
        test_location = "dict://custom_reports/"
        config.DATATESTER_INTERNAL_TESTREPORT_LOCATION = test_location

        # When: creating a ReportDependencyInjector
        injector = ReportDependencyInjector(config)

        # Then: the internal location should be correctly set
        assert injector.internal_location.path == test_location

    def test_cli_manager_with_different_user_storage(self, config):
        """Test CLI manager creation with different user storage types"""
        # Given: a configuration and domain config with LOCAL storage
        domain_config = DomainConfigDTO(
            domain="test_domain",
            instances={"test": ["alpha"]},
            specifications_locations=[LocationDTO("dict://specs")],
            testreports_location=LocationDTO("local://testreports"),
            testcases=TestCasesConfigDTO(
                schema=SchemaTestCaseConfigDTO(compare_datatypes=["int", "string"]),
                compare=CompareTestCaseConfigDTO(sample_size=100),
            ),
        )
        injector = ReportDependencyInjector(config)

        # When: creating a CLI report manager
        cli_manager = injector.cli_report_manager(domain_config)

        # Then: the user storage should be FileStorage
        assert isinstance(injector.user_storage, FileStorage)
        assert cli_manager.user_location.path == "local://testreports/"
