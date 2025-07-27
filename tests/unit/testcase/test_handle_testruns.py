import pytest
from datetime import datetime
from uuid import uuid4

from src.testcase.application.handle_testruns import TestRunCommandHandler
from src.data_platform import DummyPlatformFactory
from src.storage.formatter_factory import FormatterFactory
from src.storage.storage_factory import StorageFactory
from src.config import Config
from src.notifier import InMemoryNotifier, StdoutNotifier
from src.dtos import (
    TestRunDTO,
    TestDefinitionDTO,
    TestObjectDTO,
    TestType,
    TestStatus,
    TestResult,
    LocationDTO,
    DomainConfigDTO,
    TestRunReportDTO,
    SpecificationDTO,
    SpecificationType,
    TestCasesConfigDTO,
    SchemaTestCaseConfigDTO,
    CompareTestCaseConfigDTO,
    StorageObject,
)
from src.testcase.ports import (
    SaveTestRunCommand,
    LoadTestRunCommand,
    SetReportIdsCommand,
    ExecuteTestRunCommand,
)
from src.storage.i_storage import StorageTypeUnknownError, ObjectNotFoundError


@pytest.fixture
def dummy_platform_factory():
    """Create a DummyPlatformFactory for testing"""
    return DummyPlatformFactory()


@pytest.fixture
def storage_factory():
    """Create a StorageFactory for testing"""
    config = Config()
    formatter_factory = FormatterFactory()
    return StorageFactory(config, formatter_factory)


@pytest.fixture
def notifiers():
    """Create notifiers for testing"""
    return [InMemoryNotifier(), StdoutNotifier()]


@pytest.fixture
def testrun_command_handler(dummy_platform_factory, storage_factory, notifiers):
    """Create a TestRunCommandHandler with test dependencies"""
    return TestRunCommandHandler(
        backend_factory=dummy_platform_factory,
        notifiers=notifiers,
        storage_factory=storage_factory,
    )


@pytest.fixture
def domain_config():
    """Create a domain config for testing"""
    return DomainConfigDTO(
        domain="test_domain",
        instances={"test_stage": ["test_instance"]},
        specifications_locations=LocationDTO("dict://specs/"),
        testreports_location=LocationDTO("dict://reports/"),
        testcases=TestCasesConfigDTO(
            schema=SchemaTestCaseConfigDTO(compare_datatypes=["int", "string"]),
            compare=CompareTestCaseConfigDTO(
                sample_size=100, sample_size_per_object={}
            ),
        ),
    )


@pytest.fixture
def test_object():
    """Create a test object for testing"""
    return TestObjectDTO(
        domain="test_domain",
        stage="test_stage",
        instance="test_instance",
        name="test_table",
    )


@pytest.fixture
def test_definition(test_object, domain_config):
    """Create a test definition for testing"""
    return TestDefinitionDTO(
        testobject=test_object,
        testtype=TestType.DUMMY_OK,
        specs=[
            SpecificationDTO(
                spec_type=SpecificationType.SCHEMA,
                location=LocationDTO(path="dict://specs/"),
                testobject=test_object.name,
            )
        ],
        domain_config=domain_config,
        testrun_id=uuid4(),
        labels=["test_label"],
    )


@pytest.fixture
def testrun(test_definition):
    """Create a test run for testing"""
    return TestRunDTO(
        testrun_id=uuid4(),
        testset_id=uuid4(),
        labels=["test_label"],
        testset_name="test_testset",
        stage="test_stage",
        instance="test_instance",
        domain="test_domain",
        domain_config=test_definition.domain_config,
        start_ts=datetime.now(),
        end_ts=None,
        status=TestStatus.INITIATED,
        result=TestResult.NA,
        testdefinitions=[test_definition],
        testcase_results=[],
    )


@pytest.fixture
def storage_location():
    """Create a storage location for testing"""
    return LocationDTO("dict://testruns/")


class TestTestRunCommandHandler:
    """Test suite for TestRunCommandHandler"""

    def test_init(
        self,
        dummy_platform_factory,
        storage_factory,
        notifiers,
        testrun,
        storage_location,
    ):
        """Test TestRunCommandHandler initialization and basic functionality"""
        # Given: DummyPlatformFactory, StorageFactory, and notifiers
        # When: Creating a TestRunCommandHandler
        handler = TestRunCommandHandler(
            backend_factory=dummy_platform_factory,
            notifiers=notifiers,
            storage_factory=storage_factory,
        )

        # Then: The handler should be properly initialized
        assert handler.backend_factory == dummy_platform_factory
        assert handler.notifiers == notifiers
        assert handler.storage_factory == storage_factory


    def test_run_executes_testrun_successfully(
        self, testrun_command_handler, testrun, storage_location
    ):
        """Test that run method executes a testrun successfully"""
        # Given: A testrun and storage location
        command = ExecuteTestRunCommand(
            testrun=testrun,
            storage_location=storage_location,
        )

        # When: Executing the testrun
        result = testrun_command_handler.run(command)

        # Then: The result should be a TestRunDTO with expected properties
        assert isinstance(result, TestRunDTO)
        assert result.testrun_id == testrun.testrun_id
        assert result.status == TestStatus.FINISHED
        assert result.result == TestResult.OK
        assert len(result.testcase_results) == 1
        assert result.testcase_results[0].result == TestResult.OK

    def test_save_load_roundtrip(
        self, testrun_command_handler, testrun, storage_location, storage_factory
    ):
        """Test that save and load work together for a complete roundtrip"""
        # Given: A testrun to save and load
        save_command = SaveTestRunCommand(
            testrun=testrun,
            storage_location=storage_location,
        )
        load_command = LoadTestRunCommand(
            testrun_id=str(testrun.testrun_id),
            storage_location=storage_location,
        )

        # When: Saving and then loading the testrun
        testrun_command_handler.save(save_command)
        loaded_testrun = testrun_command_handler.load(load_command)

        # Then: The loaded testrun should be identical to the original
        assert loaded_testrun.testrun_id == testrun.testrun_id
        assert loaded_testrun.testset_name == testrun.testset_name
        assert loaded_testrun.domain == testrun.domain
        assert loaded_testrun.stage == testrun.stage
        assert loaded_testrun.instance == testrun.instance
        assert len(loaded_testrun.testdefinitions) == len(testrun.testdefinitions)
        assert len(loaded_testrun.testcase_results) == len(testrun.testcase_results)

    def test_set_report_ids_updates_testrun_and_persists(
        self, testrun_command_handler, testrun, storage_location, storage_factory
    ):
        """Test that set_report_ids updates testrun with report ID and persists it"""
        # Given: A testrun and testrun report
        report_id = uuid4()
        testrun_report = TestRunReportDTO(
            report_id=report_id,
            testrun_id=testrun.testrun_id,
            testset_id=testrun.testset_id,
            labels=testrun.labels,
            result=TestResult.OK.value,
            start_ts=datetime.now(),
            end_ts=datetime.now(),
            testcase_results=[],
        )
        command = SetReportIdsCommand(
            testrun=testrun,
            testrun_report=testrun_report,
            storage_location=storage_location,
        )

        # When: Setting report IDs
        testrun_command_handler.set_report_ids(command)

        # Then: The testrun should be updated with report ID and persisted
        storage = storage_factory.get_storage(storage_location)
        saved_testrun = storage.read(
            StorageObject.TESTRUN, str(testrun.testrun_id), storage_location
        )
        assert saved_testrun.report_id == report_id

    def test_load_raises_error_when_testrun_not_found(
        self, testrun_command_handler, storage_location
    ):
        """Test that load raises error when testrun is not found"""
        # Given: A non-existent testrun ID
        non_existent_id = str(uuid4())
        command = LoadTestRunCommand(
            testrun_id=non_existent_id,
            storage_location=storage_location,
        )

        # When/Then: Loading should raise ObjectNotFoundError
        with pytest.raises(ObjectNotFoundError):
            testrun_command_handler.load(command)

    def test_unsupported_storage_type_raises_error(
        self, testrun_command_handler, testrun
    ):
        """Test that save raises error with unsupported storage type"""
        # Given: An unsupported storage location (S3 is in enum but not supported)
        unsupported_location = LocationDTO("s3://testruns/")
        save_command = SaveTestRunCommand(
            testrun=testrun,
            storage_location=unsupported_location,
        )
        load_command = LoadTestRunCommand(
            testrun_id=str(uuid4()),
            storage_location=unsupported_location,
        )

        # Then: Saving or loading should raise StorageTypeUnknownError
        with pytest.raises(StorageTypeUnknownError):
            testrun_command_handler.save(save_command)

        with pytest.raises(StorageTypeUnknownError):
            testrun_command_handler.load(load_command)

    def test_run_with_multiple_testcases(
        self, testrun_command_handler, testrun, storage_location
    ):
        """Test that run method handles multiple testcases correctly"""
        # Given: A testrun with multiple test definitions
        testrun.testdefinitions = [
            TestDefinitionDTO(
                testobject=testrun.testdefinitions[0].testobject,
                testtype=TestType.DUMMY_OK,
                specs=testrun.testdefinitions[0].specs,
                domain_config=testrun.testdefinitions[0].domain_config,
                testrun_id=testrun.testrun_id,
                labels=["test_label"],
            ),
            TestDefinitionDTO(
                testobject=testrun.testdefinitions[0].testobject,
                testtype=TestType.DUMMY_NOK,
                specs=testrun.testdefinitions[0].specs,
                domain_config=testrun.testdefinitions[0].domain_config,
                testrun_id=testrun.testrun_id,
                labels=["test_label"],
            ),
        ]
        command = ExecuteTestRunCommand(
            testrun=testrun,
            storage_location=storage_location,
        )

        # When: Executing the testrun
        result = testrun_command_handler.run(command)

        # Then: The result should contain results for all testcases
        assert len(result.testcase_results) == 2
        assert result.testcase_results[0].result == TestResult.OK
        assert result.testcase_results[1].result == TestResult.NOK
        # And: The overall testrun result should be NA (not OK) due to NOK testcase
        assert result.result == TestResult.NA
