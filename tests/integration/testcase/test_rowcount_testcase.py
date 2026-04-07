from uuid import uuid4
from tests.conftest import DemoData
from src.domain.testrun.testcases import RowCountTestCase
from src.dtos import (
    RowcountSpecDTO,
    TestObjectDTO,
    TestType,
    SpecType,
    LocationDTO,
)
from src.dtos.testrun_dtos import TestCaseDefDTO
from src.infrastructure.backend.demo import DemoBackendFactory
from src.infrastructure.notifier import InMemoryNotifier


spec = RowcountSpecDTO(
    location=LocationDTO(path="dummy://this_location"),
    testobject="core_account_payments",
    spec_type=SpecType.ROWCOUNT,
    query="""
    WITH __expected_count__ AS (
        SELECT COUNT(*)
        FROM payments_test.alpha.stage_transactions AS transactions
        LEFT JOIN payments_test.alpha.stage_accounts AS accounts
            ON transactions.account_id = accounts.id
            AND transactions.date = accounts.date
    )
    , __actual_count__ AS (
        SELECT COUNT(*)
        FROM payments_test.alpha.core_account_payments
    )
    """,
)

testobject = TestObjectDTO(
    domain="payments",
    stage="test",
    instance="alpha",
    name="core_account_payments",
)


def test_straight_through_execution(domain_config, demo_data: DemoData):
    definition = TestCaseDefDTO(
        testobject=testobject,
        testtype=TestType.ROWCOUNT,
        specs=[spec],
        domain_config=domain_config,
    )
    backend = DemoBackendFactory(
        files_path=demo_data.raw_path,
        db_path=demo_data.db_path,
    ).create(domain_config=domain_config)
    try:
        testcase = RowCountTestCase(
            definition=definition,
            testrun_id=uuid4(),
            backend=backend,
            notifiers=[InMemoryNotifier()],
        )
        testcase.execute()
        assert testcase.result == testcase.result.OK
    finally:
        backend.close()
