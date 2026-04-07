from uuid import uuid4
from tests.conftest import DemoData
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
    domain="payments",
    stage="test",
    instance="alpha",
    name="stage_accounts",
)


def test_straight_through_execution(domain_config, demo_data: DemoData):
    """stage_accounts has no truncation, so counts should match -> OK."""
    definition = TestDefinitionDTO(
        testobject=testobject,
        testtype=TestType.STAGECOUNT,
        specs=[spec],
        domain_config=domain_config,
        testrun_id=uuid4(),
    )
    backend = DemoBackendFactory(
        files_path=demo_data.raw_path,
        db_path=demo_data.db_path,
    ).create(domain_config=domain_config)
    try:
        testcase = StageCountTestCase(
            definition=definition,
            backend=backend,
            notifiers=[InMemoryNotifier()],
        )
        testcase.execute()
        assert testcase.result == testcase.result.OK
    finally:
        backend.close()
