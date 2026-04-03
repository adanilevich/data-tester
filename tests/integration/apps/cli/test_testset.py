import pytest
import uuid

from src.apps.cli_di import CliDependencyInjector
from src.dtos.testset_dtos import TestSetDTO, TestCaseEntryDTO
from src.drivers.testset_driver import TestSetNotFoundError
from src.dtos.testcase_dtos import TestType
from src.config import Config
from src.domain_ports import SaveTestSetCommand


@pytest.fixture
def injector():
    cfg = Config()
    return CliDependencyInjector(cfg)


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


def test_load_domain_testset_by_name_success(
    injector, testset_dto
):
    cli_manager = injector.testset_driver()
    handler = injector.testset_driver().testset_handler

    # save two testsets
    save_command_1 = SaveTestSetCommand(testset=testset_dto)
    handler.save_testset(save_command_1)

    new_testset_dto = testset_dto.copy()
    new_testset_dto.name = "TestSet2"
    new_testset_dto.testset_id = uuid.uuid4()
    save_command_2 = SaveTestSetCommand(
        testset=new_testset_dto
    )
    handler.save_testset(save_command_2)

    # load first testset by domain and name
    loaded = cli_manager.load_domain_testset_by_name(
        "domain1", "TestSet1"
    )
    assert loaded.name == testset_dto.name
    assert loaded.domain == testset_dto.domain
    assert loaded.testcases == testset_dto.testcases

    # load second testset
    loaded = cli_manager.load_domain_testset_by_name(
        "domain1", "TestSet2"
    )
    assert loaded.name == new_testset_dto.name
    assert loaded.domain == new_testset_dto.domain
    assert loaded.testcases == new_testset_dto.testcases


def test_load_domain_testset_by_name_not_found(
    injector, testset_dto
):
    cli_manager = injector.testset_driver()
    handler = injector.testset_driver().testset_handler

    save_command = SaveTestSetCommand(testset=testset_dto)
    handler.save_testset(save_command)

    domain = "domain1"
    name = "NonExistentSet"
    with pytest.raises(TestSetNotFoundError) as excinfo:
        cli_manager.load_domain_testset_by_name(domain, name)
    assert (
        str(excinfo.value)
        == f"Testset with name '{name}' not found "
        f"in domain '{domain}'"
    )
