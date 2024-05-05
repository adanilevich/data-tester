from uuid import uuid4
from src.testcase.testcases import TestCaseFactory
from src.dtos import CompareSampleSqlDTO, SchemaSpecificationDTO, TestObjectDTO, TestType
from src.testcase.adapters.data_platforms import DemoDataPlatformFactory
from src.testcase.adapters.notifiers import InMemoryNotifier, StdoutNotifier


sql = CompareSampleSqlDTO(
    location="this_location",
    testobject="core_customer_transactions",
    query="""
    WITH __expected__ AS (
        SELECT
            customers.name AS customer_name,
            customers.id AS customer_id,
            transactions.id AS id,
            transactions.date AS transaction_date,
            transactions.amount AS amount
        FROM payments_test.alpha.stage_transactions AS transactions
        LEFT JOIN payments_test.alpha.stage_customers AS customers
            ON transactions.customer_id = customers.id
            AND transactions.date = customers.date
        WHERE customers.region != 'africa'
    )
    """
)

schema = SchemaSpecificationDTO(
    location="that_location",
    testobject="core_customer_transactions",
    columns={"customer_id": "int"},  # plays no role, but must be non-empty
    primary_keys=["customer_id", "transaction_date"]
)

testobject = TestObjectDTO(
    domain="payments",
    stage="test",
    instance="alpha",
    name="core_customer_transactions"
)


def test_straight_through_execution(domain_config, prepare_local_data):
    testcase = TestCaseFactory.create(
        ttype=TestType.COMPARE_SAMPLE,
        testobject=testobject,
        specs=[schema, sql],
        domain_config=domain_config,
        testrun_id=uuid4(),
        backend=DemoDataPlatformFactory().create(domain_config=domain_config),
        notifiers=[InMemoryNotifier(), StdoutNotifier()]
    )

    testcase.execute()

    assert testcase.result == testcase.result.OK
