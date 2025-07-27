import pytest
from uuid import uuid4

from src.testset.application.handle_testsets import TestSetCommandHandler
from src.dtos.testset import TestSetDTO, TestCaseEntryDTO
from src.dtos.location import LocationDTO
from src.storage import StorageFactory, FormatterFactory, ObjectNotFoundError
from src.dtos.testcase import TestType
from src.testset.ports.drivers.i_testset_handler import (
    SaveTestSetCommand,
    LoadTestSetCommand,
    ListTestSetsCommand,
)
from src.config import Config


@pytest.fixture
def storage_factory():
    config = Config()
    formatter_factory = FormatterFactory()
    return StorageFactory(config, formatter_factory)


@pytest.fixture
def handler(storage_factory):
    return TestSetCommandHandler(storage_factory)


@pytest.fixture
def testset_dto():
    testcase = TestCaseEntryDTO(
        testobject="table1",
        testtype=TestType.ROWCOUNT,
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
    # Given a handler and a testset DTO
    location = LocationDTO("dict://testsets/")
    # When saving the testset
    save_cmd = SaveTestSetCommand(testset=testset_dto, location=location)
    handler.save_testset(save_cmd)
    # Then it can be loaded back and matches the original
    load_cmd = LoadTestSetCommand(
        testset_id=str(testset_dto.testset_id), location=location
    )
    loaded = handler.load_testset(load_cmd)
    assert loaded.name == testset_dto.name
    assert loaded.domain == testset_dto.domain
    assert loaded.testcases == testset_dto.testcases


def test_list_testsets_by_domain(handler, testset_dto):
    # Given two testsets in different domains
    location = LocationDTO("dict://testsets/")
    handler.save_testset(SaveTestSetCommand(testset=testset_dto, location=location))
    other_testset = TestSetDTO(
        name="OtherSet",
        description="Other",
        labels=["label2"],
        domain="otherdomain",
        default_stage="stage2",
        default_instance="instance2",
        testcases={},
    )
    handler.save_testset(SaveTestSetCommand(testset=other_testset, location=location))
    # When listing testsets for domain1
    list_cmd = ListTestSetsCommand(location=location, domain="domain1")
    result = handler.list_testsets(list_cmd)
    # Then only the testset in domain1 is returned
    assert len(result) == 1
    assert result[0].domain == "domain1"
    assert result[0].name == testset_dto.name


def test_list_testsets_empty(handler):
    # Given an empty storage
    location = LocationDTO("dict://testsets/")
    # When listing testsets for any domain
    list_cmd = ListTestSetsCommand(location=location, domain="anydomain")
    result = handler.list_testsets(list_cmd)
    # Then the result is empty
    assert result == []


def test_load_nonexistent_testset_raises(handler):
    # Given a handler and a location
    location = LocationDTO("dict://testsets/")
    # When loading a non-existent testset
    load_cmd = LoadTestSetCommand(testset_id=str(uuid4()), location=location)
    # Then it raises an error
    with pytest.raises(ObjectNotFoundError):
        handler.load_testset(load_cmd)
