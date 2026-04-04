import pytest
from typing import cast
from uuid import uuid4
from datetime import datetime

from src.dtos import (
    TestObjectDTO,
    SpecDTO,
    TestType,
    SpecType,
    TestDefinitionDTO,
    TestRunDTO,
    TestStatus,
    TestResult,
    LocationDTO,
    ObjectType,
)
from src.domain.testrun.testrun import TestRun
from src.infrastructure.storage.dto_storage_file import MemoryDtoStorage
from src.infrastructure.storage.dto_storage_file import JsonSerializer
from src.infrastructure.backend.dummy import DummyBackend
from src.infrastructure.notifier import InMemoryNotifier


class TestTestRun:
    @pytest.fixture
    def testobject(self):
        return TestObjectDTO(
            name="to", domain="dom", stage="proj", instance="inst"
        )

    @pytest.fixture
    def specifications(self):
        return [
            SpecDTO(
                spec_type=SpecType.SCHEMA,
                location=LocationDTO(path="dummy://loc"),
                testobject="to",
            ),
            SpecDTO(
                spec_type=SpecType.ROWCOUNT,
                location=LocationDTO(path="dummy://loc"),
                testobject="to",
            ),
        ]

    @pytest.fixture
    def domain_config(self, domain_config):
        return domain_config

    @pytest.fixture
    def dto_storage(self) -> MemoryDtoStorage:
        return MemoryDtoStorage(
            serializer=JsonSerializer(),
            storage_location=LocationDTO("memory://test/"),
        )

    @pytest.fixture
    def backend(self):
        return DummyBackend()

    @pytest.fixture
    def notifier(self):
        return InMemoryNotifier()

    def make_testrun_dto(
        self, testobject, specifications, domain_config
    ):
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
        dto_storage,
        backend,
        notifier,
    ):
        testrun_dto = self.make_testrun_dto(
            testobject, specifications, domain_config
        )
        original_start_ts = testrun_dto.start_ts

        testrun = TestRun(
            testrun_dto, backend, [notifier], dto_storage
        )

        assert testrun.testrun.testrun_id == testrun_dto.testrun_id
        assert testrun.testrun.start_ts != original_start_ts
        assert testrun.testrun.end_ts is None
        assert testrun.testrun.result == TestResult.NA
        assert testrun.testrun.status == TestStatus.INITIATED
        assert testrun.testcase_results == []
        assert testrun.backend == backend
        assert testrun.notifiers == [notifier]
        assert testrun.dto_storage == dto_storage

        # Initial state should be persisted
        persisted_dto = cast(
            TestRunDTO,
            dto_storage.read_dto(
                object_type=ObjectType.TESTRUN,
                id=str(testrun_dto.testrun_id),
            ),
        )
        assert persisted_dto.testrun_id == testrun_dto.testrun_id
        assert persisted_dto.status == TestStatus.INITIATED
        assert persisted_dto.result == TestResult.NA
        assert persisted_dto.testcase_results == []

    def test_execute(
        self,
        testobject,
        specifications,
        domain_config,
        dto_storage,
        backend,
        notifier,
    ):
        testrun_dto = self.make_testrun_dto(
            testobject, specifications, domain_config
        )
        testrun = TestRun(
            testrun_dto, backend, [notifier], dto_storage
        )

        result = testrun.execute()

        results = {
            tc.testtype: tc for tc in result.testcase_results
        }
        assert results[TestType.DUMMY_OK].result == TestResult.OK
        assert results[TestType.DUMMY_NOK].result == TestResult.NOK
        assert (
            results[TestType.DUMMY_EXCEPTION].result == TestResult.NA
        )

        assert result.result == TestResult.NOK
        assert result.status == TestStatus.FINISHED

        # Final state should be persisted
        persisted_dto = cast(
            TestRunDTO,
            dto_storage.read_dto(
                object_type=ObjectType.TESTRUN,
                id=str(testrun_dto.testrun_id),
            ),
        )
        assert persisted_dto.status == TestStatus.FINISHED
        assert persisted_dto.result == TestResult.NOK
        assert persisted_dto.end_ts is not None
        assert len(persisted_dto.testcase_results) == 3

    def test_to_dto_and_persist(
        self,
        testobject,
        specifications,
        domain_config,
        dto_storage,
        backend,
        notifier,
    ):
        testrun_dto = self.make_testrun_dto(
            testobject, specifications, domain_config
        )
        testrun = TestRun(
            testrun_dto, backend, [notifier], dto_storage
        )

        dto = testrun.to_dto()
        testrun.persist()

        persisted_dto = cast(
            TestRunDTO,
            dto_storage.read_dto(
                object_type=ObjectType.TESTRUN,
                id=str(testrun_dto.testrun_id),
            ),
        )
        persisted_dto = TestRunDTO.model_validate(persisted_dto)
        assert persisted_dto.testrun_id == dto.testrun_id
        assert persisted_dto.testset_id == dto.testset_id
        assert persisted_dto.domain == dto.domain
        assert persisted_dto.stage == dto.stage
        assert persisted_dto.instance == dto.instance
        assert persisted_dto.status == dto.status
        assert persisted_dto.result == dto.result
        assert len(persisted_dto.testdefinitions) == len(
            dto.testdefinitions
        )
        assert len(persisted_dto.testcase_results) == len(
            dto.testcase_results
        )
