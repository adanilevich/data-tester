from uuid import uuid4
from tests.conftest import DemoData
from src.domain.testrun.testcases import SchemaTestCase
from src.dtos import (
    SchemaSpecDTO,
    TestObjectDTO,
    TestType,
    SpecType,
    TestDefinitionDTO,
    LocationDTO,
)
from src.infrastructure.backend.demo import DemoBackendFactory
from src.infrastructure.notifier import InMemoryNotifier

spec = SchemaSpecDTO(
    location=LocationDTO(path="dummy://this_location"),
    testobject="stage_accounts",
    spec_type=SpecType.SCHEMA,
    columns={
        "date": "string",
        "id": "int",
        "customer_id": "int",
        "type": "string",
        "name": "string",
        "m__ts": "timestamp",
        "m__source_file": "string",
        "m__source_file_path": "string",
    },
)

testobject = TestObjectDTO(
    domain="payments",
    stage="test",
    instance="alpha",
    name="stage_accounts",
)


def test_straight_through_execution(domain_config, demo_data: DemoData):
    definition = TestDefinitionDTO(
        testobject=testobject,
        testtype=TestType.SCHEMA,
        specs=[spec],
        domain_config=domain_config,
        testrun_id=uuid4(),
    )
    backend = DemoBackendFactory(
        files_path=demo_data.raw_path,
        db_path=demo_data.db_path,
    ).create(domain_config=domain_config)
    try:
        testcase = SchemaTestCase(
            definition=definition,
            backend=backend,
            notifiers=[InMemoryNotifier()],
        )
        testcase.execute()
        assert testcase.result == testcase.result.OK
    finally:
        backend.close()
