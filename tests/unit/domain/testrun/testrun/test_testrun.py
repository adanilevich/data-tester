import pytest
from typing import cast
from uuid import uuid4

from src.dtos import (
    TestObjectDTO,
    SchemaSpecDTO,
    RowcountSpecDTO,
    TestType,
    TestRunDTO,
    Status,
    Result,
    LocationDTO,
    ObjectType,
)
from src.dtos.testrun_dtos import TestCaseDefDTO, TestRunDefDTO
from src.domain.testrun.testrun import TestRun
from src.infrastructure.storage.dto_storage_file import MemoryDtoStorage
from src.infrastructure.storage.dto_storage_file import JsonSerializer
from src.infrastructure.backend.dummy import DummyBackendFactory
from src.infrastructure.notifier import InMemoryNotifier


class TestTestRun:
    @pytest.fixture
    def testobject(self):
        return TestObjectDTO(name="to", domain="dom", stage="proj", instance="inst")

    @pytest.fixture
    def specifications(self):
        return [
            SchemaSpecDTO(
                location=LocationDTO(path="dummy://loc"),
                testobject="to",
            ),
            RowcountSpecDTO(
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
    def backend_factory(self):
        return DummyBackendFactory()

    @pytest.fixture
    def notifier(self):
        return InMemoryNotifier()

    def make_testrun_def(self, testobject, specifications, domain_config):
        return TestRunDefDTO(
            testcase_defs=[
                TestCaseDefDTO(
                    testobject=testobject,
                    testtype=TestType.DUMMY_OK,
                    specs=specifications,
                    domain_config=domain_config,
                    labels=[],
                ),
                TestCaseDefDTO(
                    testobject=testobject,
                    testtype=TestType.DUMMY_NOK,
                    specs=specifications,
                    domain_config=domain_config,
                    labels=[],
                ),
                TestCaseDefDTO(
                    testobject=testobject,
                    testtype=TestType.DUMMY_EXCEPTION,
                    specs=specifications,
                    domain_config=domain_config,
                    labels=[],
                ),
            ],
            domain=testobject.domain,
            stage=testobject.stage,
            instance=testobject.instance,
            domain_config=domain_config,
        )

    def test_init(
        self,
        testobject,
        specifications,
        domain_config,
        dto_storage,
        backend_factory,
        notifier,
    ):
        testrun_def = self.make_testrun_def(testobject, specifications, domain_config)
        testrun_id = uuid4()

        testrun = TestRun(
            testrun_def, backend_factory, [notifier], dto_storage, testrun_id=testrun_id
        )

        assert testrun.id == testrun_id
        assert testrun.end_ts is None
        assert testrun.result == Result.NA
        assert testrun.status == Status.INITIATED
        assert testrun.results == []
        assert testrun.backend_factory == backend_factory
        assert testrun.notifiers == [notifier]
        assert testrun.dto_storage == dto_storage

        # Initial state should be persisted
        persisted_dto = cast(
            TestRunDTO,
            dto_storage.read_dto(
                object_type=ObjectType.TESTRUN,
                id=str(testrun_id),
            ),
        )
        assert persisted_dto.id == testrun_id
        assert persisted_dto.status == Status.INITIATED
        assert persisted_dto.result == Result.NA
        assert persisted_dto.results == []

    def test_execute(
        self,
        testobject,
        specifications,
        domain_config,
        dto_storage,
        backend_factory,
        notifier,
    ):
        testrun_def = self.make_testrun_def(testobject, specifications, domain_config)
        testrun = TestRun(testrun_def, backend_factory, [notifier], dto_storage)

        result = testrun.execute()

        results = {tc.testtype: tc for tc in result.results}
        assert results[TestType.DUMMY_OK].result == Result.OK
        assert results[TestType.DUMMY_NOK].result == Result.NOK
        assert results[TestType.DUMMY_EXCEPTION].result == Result.NA

        assert result.result == Result.NOK
        assert result.status == Status.FINISHED

        # Final state should be persisted
        persisted_dto = cast(
            TestRunDTO,
            dto_storage.read_dto(
                object_type=ObjectType.TESTRUN,
                id=str(testrun.id),
            ),
        )
        assert persisted_dto.status == Status.FINISHED
        assert persisted_dto.result == Result.NOK
        assert persisted_dto.end_ts is not None
        assert len(persisted_dto.results) == 3

    def test_to_dto_and_persist(
        self,
        testobject,
        specifications,
        domain_config,
        dto_storage,
        backend_factory,
        notifier,
    ):
        testrun_def = self.make_testrun_def(testobject, specifications, domain_config)
        testrun = TestRun(testrun_def, backend_factory, [notifier], dto_storage)

        dto = testrun.to_dto()
        testrun.persist()

        persisted_dto = cast(
            TestRunDTO,
            dto_storage.read_dto(
                object_type=ObjectType.TESTRUN,
                id=str(testrun.id),
            ),
        )
        persisted_dto = TestRunDTO.model_validate(persisted_dto)
        assert persisted_dto.id == dto.id
        assert persisted_dto.testset_id == dto.testset_id
        assert persisted_dto.domain == dto.domain
        assert persisted_dto.stage == dto.stage
        assert persisted_dto.instance == dto.instance
        assert persisted_dto.status == dto.status
        assert persisted_dto.result == dto.result
        assert len(persisted_dto.testdefinitions) == len(dto.testdefinitions)
        assert len(persisted_dto.results) == len(dto.results)
