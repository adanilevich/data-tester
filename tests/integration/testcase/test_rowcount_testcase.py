from uuid import uuid4
from src.testcase.core.testcases import RowCountTestCase
from src.dtos import (
    RowCountSqlDTO, TestObjectDTO, TestType, SpecificationType, TestDefinitionDTO
)
from src.data_platform import DemoDataPlatformFactory
from src.notifier import InMemoryNotifier, StdoutNotifier


spec = RowCountSqlDTO(
    location="this_location",
    testobject="core_customer_transactions",
    spec_type=SpecificationType.ROWCOUNT_SQL,
    query="""
    WITH __expected_count__ AS (
        SELECT COUNT(*)
        FROM payments_test.alpha.stage_transactions AS transactions
        LEFT JOIN payments_test.alpha.stage_customers AS customers
            ON transactions.customer_id = customers.id
            AND transactions.date = customers.date
        WHERE customers.region != 'africa'
    )
    , __actual_count__ AS (
        SELECT COUNT(*)
        FROM payments_test.alpha.core_customer_transactions
    )
    """
)

testobject = TestObjectDTO(
    domain="payments",
    stage="test",
    instance="alpha",
    name="core_customer_transactions"
)


def test_straight_through_execution(domain_config, prepare_local_data):
    definition = TestDefinitionDTO(
        testobject=testobject,
        testtype=TestType.ROWCOUNT,
        specs=[spec],
        domain_config=domain_config,
        testrun_id=uuid4(),
    )
    testcase = RowCountTestCase(
        definition=definition,
        backend=DemoDataPlatformFactory().create(domain_config=domain_config),
        notifiers=[InMemoryNotifier(), StdoutNotifier()]
    )

    testcase.execute()
    assert testcase.result == testcase.result.OK
