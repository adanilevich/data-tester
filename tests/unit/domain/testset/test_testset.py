import pytest
from uuid import uuid4

from src.domain.testset.testset import TestSet
from src.dtos.testset_dtos import TestSetDTO, TestCaseEntryDTO
from src.dtos import LocationDTO
from src.infrastructure.storage import ObjectNotFoundError
from src.infrastructure.storage.dto_storage_file import MemoryDtoStorage
from src.infrastructure.storage.dto_storage_file import JsonSerializer
from src.dtos.testcase_dtos import TestType


@pytest.fixture
def dto_storage() -> MemoryDtoStorage:
    return MemoryDtoStorage(
        serializer=JsonSerializer(),
        storage_location=LocationDTO("memory://test/"),
    )


@pytest.fixture
def testset_dto():
    testcase = TestCaseEntryDTO(
        testobject="table1",
        testtype=TestType.ROWCOUNT,
        comment="A test case",
    )
    testset = TestSetDTO(
        name="TestSet1",
        description="A test set",
        labels=["label1"],
        domain="domain1",
        default_stage="stage1",
        default_instance="instance1",
        testcases={testcase.identifier: testcase},
    )
    return testset


@pytest.fixture
def testset(dto_storage: MemoryDtoStorage) -> TestSet:
    return TestSet(dto_storage)


def test_save_and_load_testset(
    testset: TestSet, testset_dto: TestSetDTO
):
    testset.save_testset(testset=testset_dto)
    loaded = testset.load_testset(
        testset_id=str(testset_dto.testset_id)
    )
    assert loaded.name == testset_dto.name
    assert loaded.domain == testset_dto.domain
    assert loaded.testcases.keys() == testset_dto.testcases.keys()
    assert loaded.testcases == testset_dto.testcases


def test_list_testsets_by_domain(
    testset: TestSet, testset_dto: TestSetDTO
):
    testset.save_testset(testset_dto)
    other_testset = TestSetDTO(
        name="OtherSet",
        description="Other",
        labels=["label2"],
        domain="otherdomain",
        default_stage="stage2",
        default_instance="instance2",
        testcases={},
    )
    testset.save_testset(other_testset)
    result = testset.list_testsets("domain1")
    assert len(result) == 1
    assert result[0].domain == "domain1"
    assert result[0].name == testset_dto.name


def test_list_testsets_empty(testset: TestSet):
    result = testset.list_testsets("anydomain")
    assert result == []


def test_load_nonexistent_testset_raises(testset: TestSet):
    with pytest.raises(ObjectNotFoundError):
        testset.load_testset(str(uuid4()))
