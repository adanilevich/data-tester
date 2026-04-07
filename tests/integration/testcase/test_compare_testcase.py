from uuid import uuid4
from tests.conftest import DemoData
from src.domain.testrun.testcases import CompareTestCase
from src.dtos import (
    CompareSpecDTO,
    SchemaSpecDTO,
    TestObjectDTO,
    TestType,
    SpecType,
    TestDefinitionDTO,
    LocationDTO,
)
from src.infrastructure.backend.demo import DemoBackendFactory
from src.infrastructure.notifier import InMemoryNotifier


sql = CompareSpecDTO(
    location=LocationDTO(path="dummy://this_location"),
    testobject="core_account_payments",
    spec_type=SpecType.COMPARE,
    query="""
    WITH __expected__ AS (
        SELECT
            accounts.name AS account_name,
            accounts.id AS account_id,
            transactions.id AS id,
            transactions.date AS transaction_date,
            transactions.amount AS amount
        FROM payments_test.alpha.stage_transactions AS transactions
        LEFT JOIN payments_test.alpha.stage_accounts AS accounts
            ON transactions.account_id = accounts.id
            AND transactions.date = accounts.date
    )
    """,
)

schema = SchemaSpecDTO(
    location=LocationDTO(path="dummy://that_location"),
    testobject="core_account_payments",
    spec_type=SpecType.SCHEMA,
    columns={"account_id": "int"},  # plays no role, but must be non-empty
    primary_keys=["account_id", "transaction_date"],
)

testobject = TestObjectDTO(
    domain="payments",
    stage="test",
    instance="alpha",
    name="core_account_payments",
)


def test_straight_through_execution(domain_config, demo_data: DemoData):
    definition = TestDefinitionDTO(
        testobject=testobject,
        testtype=TestType.COMPARE,
        specs=[schema, sql],
        domain_config=domain_config,
        testrun_id=uuid4(),
    )
    backend = DemoBackendFactory(
        files_path=demo_data.raw_path,
        db_path=demo_data.db_path,
    ).create(domain_config=domain_config)
    try:
        testcase = CompareTestCase(
            definition=definition,
            backend=backend,
            notifiers=[InMemoryNotifier()],
        )
        testcase.execute()
        assert testcase.result == testcase.result.OK
    finally:
        backend.close()
