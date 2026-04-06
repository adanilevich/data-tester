from uuid import uuid4
import pytest
from tests.fixtures.demo.prepare_demo_data import (
    prepare_demo_data, clean_up_demo_data,
)
from src.domain.testrun.testcases import StageCountTestCase
from src.dtos import (
    StagecountSpecDTO,
    TestObjectDTO,
    TestType,
    SpecType,
    TestDefinitionDTO,
    LocationDTO,
)
from src.infrastructure.backend.demo import DemoBackendFactory
from src.infrastructure.notifier import InMemoryNotifier


spec = StagecountSpecDTO(
    location=LocationDTO(path="dummy://stagecount_spec"),
    testobject="stage_accounts",
    spec_type=SpecType.STAGECOUNT,
    raw_file_format="csv",
    raw_file_encoding="utf-8",
    skip_lines=1,
)

testobject = TestObjectDTO(
    domain="payments", stage="test", instance="alpha",
    name="stage_accounts",
)


@pytest.fixture(scope="module")
def prepare_demo_data_fixture():
    prepare_demo_data()
    yield
    clean_up_demo_data()


def test_straight_through_execution(domain_config, prepare_demo_data_fixture):
    """stage_accounts has no truncation, so counts should match → OK."""
    definition = TestDefinitionDTO(
        testobject=testobject,
        testtype=TestType.STAGECOUNT,
        specs=[spec],
        domain_config=domain_config,
        testrun_id=uuid4(),
    )
    testcase = StageCountTestCase(
        definition=definition,
        backend=DemoBackendFactory().create(domain_config=domain_config),
        notifiers=[InMemoryNotifier()],
    )

    testcase.execute()
    assert testcase.result == testcase.result.OK
