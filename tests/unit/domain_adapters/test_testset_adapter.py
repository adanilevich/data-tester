import pytest
from uuid import uuid4

from src.domain_adapters import TestSetAdapter
from src.dtos.testset_dtos import TestSetDTO, TestCaseEntryDTO
from src.dtos import LocationDTO
from src.infrastructure.storage import ObjectNotFoundError
from src.infrastructure.storage.dto_storage_file import MemoryDtoStorage
from src.infrastructure.storage.dto_storage_file import JsonSerializer
from src.dtos.testrun_dtos import TestType
from src.domain_ports import (
    SaveTestSetCommand,
    LoadTestSetCommand,
    ListTestSetsCommand,
)


@pytest.fixture
def dto_storage() -> MemoryDtoStorage:
    return MemoryDtoStorage(
        serializer=JsonSerializer(),
        storage_location=LocationDTO("memory://test/"),
    )


@pytest.fixture
def handler(dto_storage: MemoryDtoStorage) -> TestSetAdapter:
    return TestSetAdapter(dto_storage)


@pytest.fixture
def testset_dto():
    testcase = TestCaseEntryDTO(
        testobject="table1",
        testtype=TestType.ROWCOUNT,
        domain="any_domain",
        comment="A test case",
    )
    return TestSetDTO(
        name="TestSet1",
        description="A test set",
        labels=["label1"],
        domain="domain1",
        default_stage="stage1",
        default_instance="instance1",
        testcases={testcase.identifier: testcase},
    )


def test_save_and_load_testset(handler, testset_dto):
    save_cmd = SaveTestSetCommand(testset=testset_dto)
    handler.save_testset(save_cmd)
    load_cmd = LoadTestSetCommand(
        testset_id=str(testset_dto.testset_id)
    )
    loaded = handler.load_testset(load_cmd)
    assert loaded.name == testset_dto.name
    assert loaded.domain == testset_dto.domain
    assert loaded.testcases == testset_dto.testcases


def test_list_testsets_by_domain(handler, testset_dto):
    handler.save_testset(
        SaveTestSetCommand(testset=testset_dto)
    )
    other_testset = TestSetDTO(
        name="OtherSet",
        description="Other",
        labels=["label2"],
        domain="otherdomain",
        default_stage="stage2",
        default_instance="instance2",
        testcases={},
    )
    handler.save_testset(
        SaveTestSetCommand(testset=other_testset)
    )
    list_cmd = ListTestSetsCommand(domain="domain1")
    result = handler.list_testsets(list_cmd)
    assert len(result) == 1
    assert result[0].domain == "domain1"
    assert result[0].name == testset_dto.name


def test_list_testsets_empty(handler):
    list_cmd = ListTestSetsCommand(domain="anydomain")
    result = handler.list_testsets(list_cmd)
    assert result == []


def test_load_nonexistent_testset_raises(handler):
    load_cmd = LoadTestSetCommand(testset_id=str(uuid4()))
    with pytest.raises(ObjectNotFoundError):
        handler.load_testset(load_cmd)
