from uuid import uuid4
from src.domain.testcase.testcases import CompareTestCase
from src.dtos import (
    CompareSqlDTO,
    SchemaSpecificationDTO,
    TestObjectDTO,
    TestType,
    SpecificationType,
    TestDefinitionDTO,
    LocationDTO,
)
from src.infrastructure.backend.demo import DemoBackendFactory
from src.infrastructure.notifier import InMemoryNotifier, StdoutNotifier


sql = CompareSqlDTO(
    location=LocationDTO(path="dummy://this_location"),
    testobject="core_customer_transactions",
    spec_type=SpecificationType.COMPARE_SQL,
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
    """,
)

schema = SchemaSpecificationDTO(
    location=LocationDTO(path="dummy://that_location"),
    testobject="core_customer_transactions",
    spec_type=SpecificationType.SCHEMA,
    columns={"customer_id": "int"},  # plays no role, but must be non-empty
    primary_keys=["customer_id", "transaction_date"],
)

testobject = TestObjectDTO(
    domain="payments", stage="test", instance="alpha", name="core_customer_transactions"
)


def test_straight_through_execution(domain_config, prepare_local_data):
    definition = TestDefinitionDTO(
        testobject=testobject,
        testtype=TestType.COMPARE,
        specs=[schema, sql],
        domain_config=domain_config,
        testrun_id=uuid4(),
    )
    testcase = CompareTestCase(
        definition=definition,
        backend=DemoBackendFactory().create(domain_config=domain_config),
        notifiers=[InMemoryNotifier(), StdoutNotifier()],
    )

    testcase.execute()

    assert testcase.result == testcase.result.OK
