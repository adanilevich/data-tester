import pytest
from datetime import datetime
from uuid import uuid4

from src.domain_adapters import TestRunAdapter
from src.infrastructure.backend.dummy import DummyBackendFactory
from src.infrastructure.storage.dto_storage_file import MemoryDtoStorage
from src.infrastructure.storage.dto_storage_file import JsonSerializer
from src.infrastructure.notifier import InMemoryNotifier
from src.dtos import (
    TestRunDTO,
    TestDefinitionDTO,
    TestObjectDTO,
    TestType,
    TestStatus,
    TestResult,
    LocationDTO,
    DomainConfigDTO,
    SpecDTO,
    SpecType,
    TestCasesConfigDTO,
    SchemaTestCaseConfigDTO,
    CompareTestCaseConfigDTO,
)
from src.domain_ports import (
    SaveTestRunCommand,
    LoadTestRunCommand,
    ExecuteTestRunCommand,
)
from src.infrastructure_ports import ObjectNotFoundError


@pytest.fixture
def dummy_platform_factory():
    """Create a DummyBackendFactory for testing"""
    return DummyBackendFactory()


@pytest.fixture
def dto_storage() -> MemoryDtoStorage:
    """Create a MemoryDtoStorage for testing"""
    return MemoryDtoStorage(
        serializer=JsonSerializer(),
        storage_location=LocationDTO("memory://test/"),
    )


@pytest.fixture
def notifiers():
    """Create notifiers for testing"""
    return [InMemoryNotifier()]


@pytest.fixture
def testrun_command_handler(dummy_platform_factory, dto_storage, notifiers):
    """Create a TestRunAdapter with test dependencies"""
    return TestRunAdapter(
        backend_factory=dummy_platform_factory,
        notifiers=notifiers,
        dto_storage=dto_storage,
    )


@pytest.fixture
def domain_config():
    """Create a domain config for testing"""
    return DomainConfigDTO(
        domain="test_domain",
        instances={"test_stage": ["test_instance"]},
        specifications_locations=LocationDTO("memory://specs/"),
        testreports_location=LocationDTO("memory://reports/"),
        testcases=TestCasesConfigDTO(
            schema=SchemaTestCaseConfigDTO(compare_datatypes=["int", "string"]),
            compare=CompareTestCaseConfigDTO(sample_size=100, sample_size_per_object={}),
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
            SpecDTO(
                spec_type=SpecType.SCHEMA,
                location=LocationDTO(path="memory://specs/"),
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


class TestTestRunAdapter:
    """Test suite for TestRunAdapter"""

    def test_init(
        self,
        dummy_platform_factory,
        dto_storage,
        notifiers,
    ):
        """Test TestRunAdapter initialization"""
        handler = TestRunAdapter(
            backend_factory=dummy_platform_factory,
            notifiers=notifiers,
            dto_storage=dto_storage,
        )

        assert handler.backend_factory == dummy_platform_factory
        assert handler.notifiers == notifiers
        assert handler.dto_storage == dto_storage

    def test_run_executes_testrun_successfully(self, testrun_command_handler, testrun):
        """Test that run method executes a testrun successfully"""
        command = ExecuteTestRunCommand(testrun=testrun)

        result = testrun_command_handler.execute_testrun(command)

        assert isinstance(result, TestRunDTO)
        assert result.testrun_id == testrun.testrun_id
        assert result.status == TestStatus.FINISHED
        assert result.result == TestResult.OK
        assert len(result.testcase_results) == 1
        assert result.testcase_results[0].result == TestResult.OK

    def test_save_load_roundtrip(self, testrun_command_handler, testrun):
        """Test that save and load work together"""
        save_command = SaveTestRunCommand(testrun=testrun)
        load_command = LoadTestRunCommand(
            testrun_id=str(testrun.testrun_id),
        )

        testrun_command_handler.save_testrun(save_command)
        loaded_testrun = testrun_command_handler.load_testrun(load_command)

        assert loaded_testrun.testrun_id == testrun.testrun_id
        assert loaded_testrun.testset_name == testrun.testset_name
        assert loaded_testrun.domain == testrun.domain
        assert loaded_testrun.stage == testrun.stage
        assert loaded_testrun.instance == testrun.instance
        assert len(loaded_testrun.testdefinitions) == len(testrun.testdefinitions)
        assert len(loaded_testrun.testcase_results) == len(testrun.testcase_results)

    def test_load_raises_error_when_testrun_not_found(self, testrun_command_handler):
        """Test that load raises error when testrun is not found"""
        non_existent_id = str(uuid4())
        command = LoadTestRunCommand(
            testrun_id=non_existent_id,
        )

        with pytest.raises(ObjectNotFoundError):
            testrun_command_handler.load_testrun(command)

    def test_run_with_multiple_testcases(self, testrun_command_handler, testrun):
        """Test that run method handles multiple testcases"""
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
        command = ExecuteTestRunCommand(testrun=testrun)

        result = testrun_command_handler.execute_testrun(command)

        assert len(result.testcase_results) == 2
        assert result.testcase_results[0].result == TestResult.OK
        assert result.testcase_results[1].result == TestResult.NOK
        assert result.result == TestResult.NOK
