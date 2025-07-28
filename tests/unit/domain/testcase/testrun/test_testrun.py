import pytest
from uuid import uuid4
from datetime import datetime

from src.dtos import (
    TestObjectDTO,
    SpecificationDTO,
    TestType,
    SpecificationType,
    TestDefinitionDTO,
    TestRunDTO,
    TestStatus,
    TestResult,
    LocationDTO,
    StorageObject,
)
from src.domain.testcase.core.testrun import TestRun
from src.infrastructure.storage import FormatterFactory, StorageFactory
from src.infrastructure.backend.dummy import DummyBackend
from src.infrastructure.notifier import InMemoryNotifier
from src.config import Config


class TestTestRun:
    @pytest.fixture
    def testobject(self):
        return TestObjectDTO(name="to", domain="dom", stage="proj", instance="inst")

    @pytest.fixture
    def specifications(self):
        return [
            SpecificationDTO(
                spec_type=SpecificationType.SCHEMA,
                location=LocationDTO(path="dummy://loc"),
                testobject="to",
            ),
            SpecificationDTO(
                spec_type=SpecificationType.ROWCOUNT_SQL,
                location=LocationDTO(path="dummy://loc"),
                testobject="to",
            ),
        ]

    @pytest.fixture
    def domain_config(self, domain_config):
        return domain_config

    @pytest.fixture
    def storage_factory(self):
        config = Config()
        formatter_factory = FormatterFactory()
        return StorageFactory(config, formatter_factory)

    @pytest.fixture
    def backend(self):
        return DummyBackend()

    @pytest.fixture
    def notifier(self):
        return InMemoryNotifier()

    @pytest.fixture
    def storage_location(self):
        return LocationDTO("dict://testruns/")

    def make_testrun_dto(self, testobject, specifications, domain_config):
        return TestRunDTO(
            testrun_id=uuid4(),
            testset_id=uuid4(),
            report_id=None,
            domain=testobject.domain,
            stage=testobject.stage,
            instance=testobject.instance,
            testset_name="testset",
            labels=[],
            domain_config=domain_config,
            start_ts=datetime.now(),
            end_ts=None,
            status=TestStatus.NOT_STARTED,
            result=TestResult.NA,
            testdefinitions=[
                TestDefinitionDTO(
                    testobject=testobject,
                    testtype=TestType.DUMMY_OK,
                    specs=specifications,
                    domain_config=domain_config,
                    testrun_id=uuid4(),
                ),
                TestDefinitionDTO(
                    testobject=testobject,
                    testtype=TestType.DUMMY_NOK,
                    specs=specifications,
                    domain_config=domain_config,
                    testrun_id=uuid4(),
                ),
                TestDefinitionDTO(
                    testobject=testobject,
                    testtype=TestType.DUMMY_EXCEPTION,
                    specs=specifications,
                    domain_config=domain_config,
                    testrun_id=uuid4(),
                ),
            ],
            testcase_results=[],
        )

    def test_init(
        self,
        testobject,
        specifications,
        domain_config,
        storage_factory,
        backend,
        notifier,
        storage_location,
    ):
        # Given a TestRunDTO with test definitions
        testrun_dto = self.make_testrun_dto(testobject, specifications, domain_config)
        original_start_ts = testrun_dto.start_ts

        # When TestRun is initialized
        testrun = TestRun(
            testrun_dto, backend, [notifier], storage_factory, storage_location
        )

        # Then the TestRun should be properly initialized
        assert testrun.testrun.testrun_id == testrun_dto.testrun_id
        assert testrun.testrun.testset_id == testrun_dto.testset_id
        assert testrun.testrun.domain == testrun_dto.domain
        assert testrun.testrun.stage == testrun_dto.stage
        assert testrun.testrun.instance == testrun_dto.instance
        assert testrun.testrun.testset_name == testrun_dto.testset_name
        assert testrun.testrun.labels == testrun_dto.labels
        assert testrun.testrun.domain_config == testrun_dto.domain_config
        assert testrun.testrun.testdefinitions == testrun_dto.testdefinitions

        # Dynamic fields should be set correctly
        assert testrun.testrun.start_ts != original_start_ts
        assert testrun.testrun.end_ts is None
        assert testrun.testrun.result == TestResult.NA
        assert testrun.testrun.status == TestStatus.INITIATED

        # Testcase results should be empty initially
        assert testrun.testcase_results == []

        # Backend, notifiers, storage, and storage_location should be set
        assert testrun.backend == backend
        assert testrun.notifiers == [notifier]
        assert testrun.storage_factory == storage_factory
        assert testrun.storage_location == storage_location

        # And the initial state should be persisted
        storage = storage_factory.get_storage(storage_location)
        persisted_dto = storage.read(
            object_type=StorageObject.TESTRUN,
            object_id=str(testrun_dto.testrun_id),
            location=storage_location,
        )

        # Verify persisted data matches the initialized state
        assert persisted_dto.testrun_id == testrun_dto.testrun_id
        assert persisted_dto.testset_id == testrun_dto.testset_id
        assert persisted_dto.domain == testrun_dto.domain
        assert persisted_dto.stage == testrun_dto.stage
        assert persisted_dto.instance == testrun_dto.instance
        assert persisted_dto.testset_name == testrun_dto.testset_name
        assert persisted_dto.labels == testrun_dto.labels
        assert persisted_dto.status == TestStatus.INITIATED
        assert persisted_dto.result == TestResult.NA
        assert persisted_dto.testcase_results == []
        assert len(persisted_dto.testdefinitions) == len(testrun_dto.testdefinitions)

    def test_execute(
        self,
        testobject,
        specifications,
        domain_config,
        storage_factory,
        backend,
        notifier,
        storage_location,
    ):
        # Given a TestRunDTO with DummyOk, DummyNok, and DummyException testcases
        testrun_dto = self.make_testrun_dto(testobject, specifications, domain_config)
        testrun = TestRun(
            testrun_dto, backend, [notifier], storage_factory, storage_location
        )

        # When execute is called
        result = testrun.execute()

        # Then the results should be as expected for each testcase
        results = {tc.testtype: tc for tc in result.testcase_results}
        assert results[TestType.DUMMY_OK].result == TestResult.OK
        assert results[TestType.DUMMY_OK].status.name == "FINISHED"
        assert results[TestType.DUMMY_NOK].result == TestResult.NOK
        assert results[TestType.DUMMY_NOK].status.name == "FINISHED"
        assert results[TestType.DUMMY_EXCEPTION].result == TestResult.NA
        assert results[TestType.DUMMY_EXCEPTION].status.name == "ERROR"

        # The overall testrun result should be NA (since not all are OK)
        assert result.result == TestResult.NA
        assert result.status == TestStatus.FINISHED

        # And the final state should be persisted correctly
        storage = storage_factory.get_storage(storage_location)
        persisted_dto = storage.read(
            object_type=StorageObject.TESTRUN,
            object_id=str(testrun_dto.testrun_id),
            location=storage_location,
        )

        # Verify persisted data matches the execution result
        assert persisted_dto.testrun_id == result.testrun_id
        assert persisted_dto.testset_id == result.testset_id
        assert persisted_dto.domain == result.domain
        assert persisted_dto.stage == result.stage
        assert persisted_dto.instance == result.instance
        assert persisted_dto.testset_name == result.testset_name
        assert persisted_dto.labels == result.labels
        assert persisted_dto.status == TestStatus.FINISHED
        assert persisted_dto.result == TestResult.NA
        assert persisted_dto.end_ts is not None  # Should be set after execution

        # Verify testcase results are persisted correctly
        assert len(persisted_dto.testcase_results) == 3
        persisted_results = {tc.testtype: tc for tc in persisted_dto.testcase_results}

        assert persisted_results[TestType.DUMMY_OK].result == TestResult.OK
        assert persisted_results[TestType.DUMMY_OK].status.name == "FINISHED"
        assert persisted_results[TestType.DUMMY_NOK].result == TestResult.NOK
        assert persisted_results[TestType.DUMMY_NOK].status.name == "FINISHED"
        assert persisted_results[TestType.DUMMY_EXCEPTION].result == TestResult.NA
        assert persisted_results[TestType.DUMMY_EXCEPTION].status.name == "ERROR"

        # Verify testdefinitions are persisted correctly
        assert len(persisted_dto.testdefinitions) == len(result.testdefinitions)

    def test_to_dto_and_persist(
        self,
        testobject,
        specifications,
        domain_config,
        storage_factory,
        backend,
        notifier,
        storage_location,
    ):
        # Given a TestRunDTO and TestRun
        testrun_dto = self.make_testrun_dto(testobject, specifications, domain_config)
        testrun = TestRun(
            testrun_dto, backend, [notifier], storage_factory, storage_location
        )

        # When to_dto is called no exception should be raised
        dto = testrun.to_dto()

        # When persist is called
        testrun.persist()

        # Then the file should exist in storage and all attributes should match
        storage = storage_factory.get_storage(storage_location)
        persisted_dto = storage.read(
            object_type=StorageObject.TESTRUN,
            object_id=str(testrun_dto.testrun_id),
            location=storage_location,
        )

        persisted_dto = TestRunDTO.model_validate(persisted_dto)
        # Check all top-level fields
        assert persisted_dto.testrun_id == dto.testrun_id
        assert persisted_dto.testset_id == dto.testset_id
        assert persisted_dto.report_id == dto.report_id
        assert persisted_dto.domain == dto.domain
        assert persisted_dto.stage == dto.stage
        assert persisted_dto.instance == dto.instance
        assert persisted_dto.testset_name == dto.testset_name
        assert persisted_dto.labels == dto.labels
        assert persisted_dto.status == dto.status
        assert persisted_dto.result == dto.result
        assert persisted_dto.start_ts == dto.start_ts

        # Check testdefinitions and testcase_results lengths
        assert len(persisted_dto.testdefinitions) == len(dto.testdefinitions)
        assert len(persisted_dto.testcase_results) == len(dto.testcase_results)
        # Check domain_config fields
        for key in dto.domain_config.__dict__:
            if key in persisted_dto.domain_config.__dict__:
                assert persisted_dto.domain_config.__dict__[key] == getattr(
                    dto.domain_config, key
                )
