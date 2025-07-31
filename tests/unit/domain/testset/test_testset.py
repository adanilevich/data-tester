import pytest
from uuid import uuid4

from src.domain.testset.testset import TestSet
from src.dtos.testset import TestSetDTO, TestCaseEntryDTO
from src.dtos.location import LocationDTO
from src.infrastructure.storage import (
    ObjectNotFoundError,
    StorageFactory,
    FormatterFactory,
)
from src.dtos.testcase import TestType


@pytest.fixture
def storage_factory():
    formatter_factory = FormatterFactory()
    return StorageFactory(formatter_factory)


@pytest.fixture
def testset_dto():
    # Given a simple testset DTO
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
def testset(storage_factory):
    return TestSet(storage_factory)


def test_save_and_load_testset(testset, testset_dto):
    # Given a testset and a dict storage
    location = LocationDTO("dict://testsets/")
    # When saving the testset
    testset.save_testset(testset=testset_dto, location=location)
    # Then it can be loaded back and matches the original
    loaded = testset.retrieve_testset(
        testset_id=str(testset_dto.testset_id), location=location
    )
    assert loaded.name == testset_dto.name
    assert loaded.domain == testset_dto.domain
    assert loaded.testcases.keys() == testset_dto.testcases.keys()
    assert loaded.testcases == testset_dto.testcases


def test_list_testsets_by_domain(testset, testset_dto):
    # Given two testsets in different domains
    location = LocationDTO("dict://testsets/")
    testset.save_testset(testset_dto, location)
    other_testset = TestSetDTO(
        name="OtherSet",
        description="Other",
        labels=["label2"],
        domain="otherdomain",
        default_stage="stage2",
        default_instance="instance2",
        testcases={},
    )
    testset.save_testset(other_testset, location)
    # When listing testsets for domain1
    result = testset.list_testsets(location, "domain1")
    # Then only the testset in domain1 is returned
    assert len(result) == 1
    assert result[0].domain == "domain1"
    assert result[0].name == testset_dto.name


def test_list_testsets_empty(testset):
    # Given an empty storage
    location = LocationDTO("dict://testsets/")
    # When listing testsets for any domain
    result = testset.list_testsets(location, "anydomain")
    # Then the result is empty
    assert result == []


def test_load_nonexistent_testset_raises(testset):
    # Given a testset core and a location
    location = LocationDTO("dict://testsets/")
    # When loading a non-existent testset
    # Then it raises an error
    with pytest.raises(ObjectNotFoundError):
        testset.retrieve_testset(str(uuid4()), location)
