from uuid import uuid4
from src.testcase.core.testcases import TestCaseFactory
from src.dtos import SchemaSpecificationDTO, TestObjectDTO, TestType
from src.data_platform import DemoDataPlatformFactory
from src.notifier import InMemoryNotifier, StdoutNotifier

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
        ttype=TestType.SCHEMA,
        testobject=testobject,
        specs=[spec],
        domain_config=domain_config,
        testrun_id=uuid4(),
        backend=DemoDataPlatformFactory().create(domain_config=domain_config),
        notifiers=[InMemoryNotifier(), StdoutNotifier()]
    )

    testcase.execute()
    assert testcase.result == testcase.result.OK
