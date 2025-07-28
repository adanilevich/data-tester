from uuid import uuid4
from src.domain.testcase.core.testcases import SchemaTestCase
from src.dtos import (
    SchemaSpecificationDTO,
    TestObjectDTO,
    TestType,
    SpecificationType,
    TestDefinitionDTO,
    LocationDTO,
)
from src.infrastructure.backend.demo import DemoBackendFactory
from src.infrastructure.notifier import InMemoryNotifier, StdoutNotifier

spec = SchemaSpecificationDTO(
    location=LocationDTO(path="dummy://this_location"),
    testobject="stage_customers",
    spec_type=SpecificationType.SCHEMA,
    columns={
        "date": "string",
        "id": "int",
        "region": "string",
        "name": "string",
        "source_file": "string",
        "type": "string",
    },
)

testobject = TestObjectDTO(
    domain="payments", stage="test", instance="alpha", name="stage_customers"
)


def test_straight_through_execution(domain_config, prepare_local_data):
    definition = TestDefinitionDTO(
        testobject=testobject,
        testtype=TestType.SCHEMA,
        specs=[spec],
        domain_config=domain_config,
        testrun_id=uuid4(),
    )
    testcase = SchemaTestCase(
        definition=definition,
        backend=DemoBackendFactory().create(domain_config=domain_config),
        notifiers=[InMemoryNotifier(), StdoutNotifier()],
    )

    testcase.execute()
    assert testcase.result == testcase.result.OK
