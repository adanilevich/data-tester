import pytest

from src.testset.dependency_injection import CliTestSetDependencyInjector
from src.dtos.testset import TestSetDTO, TestCaseEntryDTO
from src.dtos.location import LocationDTO
from src.dtos.testcase import TestType
from src.config import Config


@pytest.fixture
def config():
    cfg = Config()
    cfg.INTERNAL_STORAGE_ENGINE = "DICT"
    cfg.INTERNAL_TESTSET_LOCATION = "dict://testsets/"
    return cfg


@pytest.fixture
def injector(config):
    return CliTestSetDependencyInjector(config)


@pytest.fixture
def cli_manager(injector):
    return injector.testset_manager()


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


def test_load_domain_testset_by_name_success(cli_manager, injector, testset_dto):
    # Given a testset saved in DictStorage for a specific domain and name
    handler = injector.testset_manager().testset_handler
    location = injector.storage_location
    storage = handler.storage
    location = LocationDTO("dict://testsets/").append(
        str(testset_dto.testset_id) + ".json"
    )
    storage.write(content=testset_dto.to_json().encode(), path=location)

    # When loading the testset by domain and name
    loaded = cli_manager.load_domain_testset_by_name("domain1", "TestSet1")
    # Then the loaded testset matches the original
    assert loaded.name == testset_dto.name
    assert loaded.domain == testset_dto.domain
    assert loaded.testcases == testset_dto.testcases


def test_load_domain_testset_by_name_not_found(cli_manager):
    # Given no testsets in storage
    # When loading a testset by domain and name that does not exist
    # Then a ValueError is raised with the correct message
    domain = "domain1"
    name = "NonExistentSet"
    with pytest.raises(ValueError) as excinfo:
        cli_manager.load_domain_testset_by_name(domain, name)
    assert (
        str(excinfo.value) == f"Testset with name '{name}' not found in domain '{domain}'"
    )
