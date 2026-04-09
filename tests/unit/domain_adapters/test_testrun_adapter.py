from uuid import uuid4

import pytest
from src.domain_adapters import TestRunAdapter
from src.domain_ports import (
    ExecuteTestRunCommand,
    LoadTestRunCommand,
    SaveTestRunCommand,
)
from src.dtos import (
    DomainConfigDTO,
    LocationDTO,
    Result,
    SchemaSpecDTO,
    Status,
    TestObjectDTO,
    TestRunDTO,
    TestType,
)
from src.dtos.testrun_dtos import TestCaseDefDTO, TestRunDefDTO
from src.infrastructure.backend.dummy import DummyBackendFactory
from src.infrastructure.notifier import InMemoryNotifier
from src.infrastructure.storage.dto_storage_file import JsonSerializer, MemoryDtoStorage
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
        spec_locations={"test_stage": ["memory://specs/"]},
        reports_location=LocationDTO("memory://reports/"),
        compare_datatypes=["int", "string"],
        sample_size_default=100,
        sample_size_per_object={},
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
def testcase_def(test_object, domain_config):
    """Create a testcase definition for testing"""
    return TestCaseDefDTO(
        testobject=test_object,
        testtype=TestType.DUMMY_OK,
        specs=[
            SchemaSpecDTO(
                location=LocationDTO(path="memory://specs/"),
                testobject=test_object.name,
            )
        ],
        domain_config=domain_config,
        labels=["test_label"],
    )


@pytest.fixture
def testrun_def(testcase_def, domain_config):
    """Create a testrun definition for testing"""
    return TestRunDefDTO(
        testcase_defs=[testcase_def],
        domain="test_domain",
        stage="test_stage",
        instance="test_instance",
        domain_config=domain_config,
        labels=["test_label"],
        testset_name="test_testset",
    )


@pytest.fixture
def testrun(testrun_def, dto_storage, dummy_platform_factory, notifiers):
    """Create and persist an initial testrun for save/load tests"""
    from src.domain.testrun.testrun import TestRun

    testrun_id = uuid4()
    tr = TestRun(
        testrun_def=testrun_def,
        backend_factory=dummy_platform_factory,
        notifiers=notifiers,
        dto_storage=dto_storage,
        testrun_id=testrun_id,
    )
    return tr.to_dto()


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

    def test_run_executes_testrun_successfully(
        self, testrun_command_handler, testrun_def
    ):
        """Test that run method executes a testrun successfully"""
        command = ExecuteTestRunCommand(testrun_def=testrun_def)

        result = testrun_command_handler.execute_testrun(command)

        assert isinstance(result, TestRunDTO)
        assert result.status == Status.FINISHED
        assert result.result == Result.OK
        assert len(result.results) == 1
        assert result.results[0].result == Result.OK

    def test_save_load_roundtrip(self, testrun_command_handler, testrun):
        """Test that save and load work together"""
        save_command = SaveTestRunCommand(testrun=testrun)
        load_command = LoadTestRunCommand(testrun_id=str(testrun.id))

        testrun_command_handler.save_testrun(save_command)
        loaded_testrun = testrun_command_handler.load_testrun(load_command)

        assert loaded_testrun.id == testrun.id
        assert loaded_testrun.testset_name == testrun.testset_name
        assert loaded_testrun.domain == testrun.domain
        assert loaded_testrun.stage == testrun.stage
        assert loaded_testrun.instance == testrun.instance
        assert len(loaded_testrun.testdefinitions) == len(testrun.testdefinitions)
        assert len(loaded_testrun.results) == len(testrun.results)

    def test_load_raises_error_when_testrun_not_found(self, testrun_command_handler):
        """Test that load raises error when testrun is not found"""
        non_existent_id = str(uuid4())
        command = LoadTestRunCommand(testrun_id=non_existent_id)

        with pytest.raises(ObjectNotFoundError):
            testrun_command_handler.load_testrun(command)

    def test_run_with_multiple_testcases(
        self, testrun_command_handler, testcase_def, domain_config
    ):
        """Test that run method handles multiple testcases"""
        test_object = testcase_def.testobject
        testrun_def = TestRunDefDTO(
            testcase_defs=[
                TestCaseDefDTO(
                    testobject=test_object,
                    testtype=TestType.DUMMY_OK,
                    specs=testcase_def.specs,
                    domain_config=domain_config,
                    labels=["test_label"],
                ),
                TestCaseDefDTO(
                    testobject=test_object,
                    testtype=TestType.DUMMY_NOK,
                    specs=testcase_def.specs,
                    domain_config=domain_config,
                    labels=["test_label"],
                ),
            ],
            domain="test_domain",
            stage="test_stage",
            instance="test_instance",
            domain_config=domain_config,
        )
        command = ExecuteTestRunCommand(testrun_def=testrun_def)

        result = testrun_command_handler.execute_testrun(command)

        assert len(result.results) == 2
        results_by_type = {tc.testtype: tc for tc in result.results}
        assert results_by_type[TestType.DUMMY_OK].result == Result.OK
        assert results_by_type[TestType.DUMMY_NOK].result == Result.NOK
        assert result.result == Result.NOK
