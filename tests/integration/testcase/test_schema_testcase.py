from src.testcase.testcases import TestCaseFactory
from src.dtos.specifications import SchemaSpecificationDTO
from src.dtos.testcase import TestObjectDTO
from src.testcase.driven_adapters.backends.local import LocalBackendFactory
from src.testcase.driven_adapters.notifiers import InMemoryNotifier, StdoutNotifier

spec = SchemaSpecificationDTO(
    location="this_location", columns={
        "date": "string", "id": "int", "region": "string", "name": "string",
        "source_file": "string", "type": "string"}
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
        backend=LocalBackendFactory().create(domain_config=domain_config),
        notifiers=[InMemoryNotifier(), StdoutNotifier()]
    )

    testcase.execute()
    assert testcase.result == testcase.result.OK
