from src.testcase.testcases import TestCaseFactory
from src.dtos import SchemaSpecificationDTO, TestObjectDTO
from src.testcase.adapters.data_platforms import LocalDataPlatformFactory
from src.testcase.adapters.notifiers import InMemoryNotifier, StdoutNotifier

spec = SchemaSpecificationDTO(
    location="this_location",
    testobject="stage_customers",
    columns={
        "date": "string", "id": "int", "region": "string", "name": "string",
        "source_file": "string", "type": "string"
    }
)

testobject = TestObjectDTO(
    domain="payments", stage="test", instance="alpha", name="stage_customers")


def test_straight_through_execution(domain_config, prepare_local_data):
    testcase = TestCaseFactory.create(
        ttype="SCHEMA",
        testobject=testobject,
        specs=[spec],
        domain_config=domain_config,
        run_id="my_run_id",
        backend=LocalDataPlatformFactory().create(domain_config=domain_config),
        notifiers=[InMemoryNotifier(), StdoutNotifier()]
    )

    testcase.execute()
    assert testcase.result == testcase.result.OK
