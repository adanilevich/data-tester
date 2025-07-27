import pytest
import uuid

from src.testset.dependency_injection import TestSetDependencyInjector
from src.dtos.testset import TestSetDTO, TestCaseEntryDTO
from src.dtos.testcase import TestType
from src.config import Config
from src.testset.ports import SaveTestSetCommand


@pytest.fixture
def injector():
    cfg = Config()
    cfg.DATATESTER_INTERNAL_STORAGE_ENGINE = "DICT"
    cfg.DATATESTER_INTERNAL_TESTSET_LOCATION = "dict://testsets/"
    return TestSetDependencyInjector(cfg)


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


def test_load_domain_testset_by_name_success(injector, testset_dto):
    # given an injector which provides a cli testset manager with a testset handler
    cli_manager = injector.cli_testset_manager()
    handler = injector.cli_testset_manager().testset_handler

    # when two testsets are saved in the configured storage location
    location = cli_manager.storage_location
    save_command_1 = SaveTestSetCommand(
        testset=testset_dto, location=location
    )
    handler.save_testset(save_command_1)

    new_testset_dto = testset_dto.copy()
    new_testset_dto.name = "TestSet2"
    new_testset_dto.testset_id = uuid.uuid4()
    save_command_2 = SaveTestSetCommand(
        testset=new_testset_dto, location=location
    )
    handler.save_testset(save_command_2)

    # When loading first testset by domain and name
    loaded = cli_manager.load_domain_testset_by_name("domain1", "TestSet1")
    # Then the loaded testset matches the original
    assert loaded.name == testset_dto.name
    assert loaded.domain == testset_dto.domain
    assert loaded.testcases == testset_dto.testcases

    # When loading second testset by domain and name
    loaded = cli_manager.load_domain_testset_by_name("domain1", "TestSet2")
    # Then the loaded testset matches the original
    assert loaded.name == new_testset_dto.name
    assert loaded.domain == new_testset_dto.domain
    assert loaded.testcases == new_testset_dto.testcases


def test_load_domain_testset_by_name_not_found(injector, testset_dto):
    # given an injector which provides a cli testset manager with a testset handler
    cli_manager = injector.cli_testset_manager()
    handler = injector.cli_testset_manager().testset_handler

    # when saving a testset
    save_command = SaveTestSetCommand(
        testset=testset_dto, location=cli_manager.storage_location
    )
    handler.save_testset(save_command)

    # when loading a testset by domain and name that does not exist
    # then a ValueError is raised with the correct message
    domain = "domain1"
    name = "NonExistentSet"
    with pytest.raises(ValueError) as excinfo:
        cli_manager.load_domain_testset_by_name(domain, name)
    assert (
        str(excinfo.value) == f"Testset with name '{name}' not found in domain '{domain}'"
    )
