from uuid import uuid4
import pytest
from tests.fixtures.demo.prepare_demo_data import (
    prepare_demo_data,
    clean_up_demo_data,
)
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


@pytest.fixture(scope="module")
def prepare_demo_data_fixture():
    prepare_demo_data()
    yield
    clean_up_demo_data()


def test_straight_through_execution(domain_config, prepare_demo_data_fixture):
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
        notifiers=[InMemoryNotifier()],
    )

    testcase.execute()
    assert testcase.result == testcase.result.OK
