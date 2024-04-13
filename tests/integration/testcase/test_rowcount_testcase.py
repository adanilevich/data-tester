from src.testcase.testcases import TestCaseFactory
from src.dtos.specifications import RowCountSqlDTO
from src.dtos.testcase import TestObjectDTO
from src.testcase.driven_adapters.backends.local import LocalBackendFactory
from src.testcase.driven_adapters.notifiers import InMemoryNotifier, StdoutNotifier


spec = RowCountSqlDTO(
    location="this_location",
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
    testcase = TestCaseFactory.create(
        ttype="ROWCOUNT",
        testobject=testobject,
        specs=[spec],
        domain_config=domain_config,
        run_id="my_run_id",
        backend=LocalBackendFactory().create(domain_config=domain_config),
        notifiers=[InMemoryNotifier(), StdoutNotifier()]
    )

    testcase.execute()
    assert testcase.result == testcase.result.OK