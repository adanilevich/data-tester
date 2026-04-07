from typing import List
import pytest
import polars as pl

from tests.conftest import DemoData
from src.infrastructure.backend.demo import (
    DemoBackendFactory,
    DemoBackendError,
)
from src.dtos import (
    DBInstanceDTO,
    TestObjectDTO,
    SchemaSpecDTO,
    SpecType,
    LocationDTO,
)


@pytest.fixture
def backend_factory(demo_data: DemoData) -> DemoBackendFactory:
    return DemoBackendFactory(files_path=demo_data.raw_path, db_path=demo_data.db_path)


@pytest.fixture
def backend(domain_config, backend_factory):
    b = backend_factory.create(domain_config=domain_config)
    try:
        yield b
    finally:
        b.close()


class TestDemoBackendFactory:
    def test_backend_creation(self, domain_config, backend_factory):
        with backend_factory.create(domain_config=domain_config) as backend:
            assert backend.config == domain_config


class TestDemoBackend:
    db = DBInstanceDTO(domain="payments", stage="test", instance="alpha")

    @pytest.fixture
    def test_query(self):
        return """
            WITH __expected__ AS (
            SELECT *
            FROM payments_test.alpha.core_account_payments
            )
        """

    @pytest.mark.parametrize(
        "domain,stage,instance,testobjects_expected",
        [
            (
                "payments",
                "uat",
                "main",
                [
                    "raw_accounts",
                    "raw_transactions",
                    "stage_accounts",
                    "stage_transactions",
                    "core_account_payments",
                ],
            ),
            (
                "sales",
                "test",
                "main",
                [
                    "raw_customers",
                    "raw_transactions",
                    "stage_customers",
                    "stage_transactions",
                    "core_customer_transactions",
                    "mart_customer_revenues_by_date",
                ],
            ),
            (
                "payments",
                "test",
                "alpha",
                [
                    "raw_accounts",
                    "raw_transactions",
                    "stage_accounts",
                    "stage_transactions",
                    "core_account_payments",
                    "mart_account_payments_by_date",
                ],
            ),
        ],
    )
    def test_getting_testobjects(
        self,
        backend,
        domain,
        stage,
        instance,
        testobjects_expected,
    ):
        db = DBInstanceDTO(domain=domain, stage=stage, instance=instance)
        testobjects_obtained = backend.list_testobjects(db)
        names_obtained = [t.name for t in testobjects_obtained]
        assert set(names_obtained) == set(testobjects_expected)
        for t in testobjects_obtained:
            assert t.domain == domain
            assert t.stage == stage
            assert t.instance == instance

    def test_getting_schema_of_file_objects_fails(self, backend):
        testobject = TestObjectDTO(
            name="raw_accounts",
            domain="payments",
            stage="test",
            instance="alpha",
        )
        with pytest.raises(DemoBackendError) as err:
            _ = backend.get_schema(testobject)
        assert "Getting schema for file-like testobjects" in str(err)

    def test_getting_schema_of_db_objects(self, backend):
        testobject = TestObjectDTO(
            name="stage_accounts",
            domain="payments",
            stage="test",
            instance="alpha",
        )
        schema = backend.get_schema(testobject)
        assert set(schema.columns.keys()) == {
            "date",
            "id",
            "customer_id",
            "type",
            "name",
            "m__ts",
            "m__source_file",
            "m__source_file_path",
        }

    def test_getting_harmonized_schema_of_db_objects(self, backend):
        testobject = TestObjectDTO(
            name="stage_accounts",
            domain="payments",
            stage="test",
            instance="alpha",
        )
        schema = backend.get_schema(testobject)
        harmonized = backend.harmonize_schema(schema)
        harmonized.columns.update({"complex": "array<string>"})

        assert harmonized.columns["date"] == "string"
        assert harmonized.columns["id"] == "int"
        assert harmonized.columns["customer_id"] == "int"
        assert harmonized.columns["complex"] == "array<string>"

    def test_getting_sample_keys_fails_without_pks(
        self,
        backend,
        test_query,
    ):
        primary_keys: List[str] = []
        with pytest.raises(DemoBackendError) as err:
            _ = backend.get_sample_keys(
                query=test_query,
                primary_keys=primary_keys,
                sample_size=5,
                db=self.db,
            )
        assert "Provide a non-empty list of primary keys" in str(err)

    def test_that_unique_keys_are_sampled(self, backend, test_query):
        primary_keys = ["id"]
        key_sample = backend.get_sample_keys(
            query=test_query,
            primary_keys=primary_keys,
            sample_size=5,
            db=self.db,
        )
        assert len(key_sample) == 5
        assert len(set(key_sample)) == 5

    def test_key_sampling_with_underspecified_keys(self, backend, test_query):
        primary_keys = ["account_id", "customer_id"]
        key_sample = backend.get_sample_keys(
            query=test_query,
            primary_keys=primary_keys,
            sample_size=2,
            db=self.db,
        )
        assert len(key_sample) == 2
        for concat_key in key_sample:
            assert len(concat_key.split("|")) == 2

    def test_sampling_from_query(self, backend, test_query):
        primary_keys = ["id", "account_id"]
        key_sample = backend.get_sample_keys(
            query=test_query,
            primary_keys=primary_keys,
            sample_size=3,
            db=self.db,
        )
        sample = backend.get_sample_from_query(
            query=test_query,
            primary_keys=primary_keys,
            key_sample=key_sample,
            db=self.db,
        )
        assert len(sample) == 3

    def test_sampling_from_testobject(self, backend):
        testobject = TestObjectDTO(
            name="core_account_payments",
            domain="payments",
            stage="test",
            instance="alpha",
        )
        primary_keys = ["id", "account_id"]
        key_sample = backend.get_sample_keys(
            query="""
                WITH __expected__ AS (
                SELECT *
                FROM payments_test.alpha.core_account_payments
                )
            """,
            primary_keys=primary_keys,
            sample_size=3,
            db=self.db,
        )
        sample = backend.get_sample_from_testobject(
            testobject=testobject,
            primary_keys=primary_keys,
            key_sample=key_sample,
        )
        assert len(sample) == 3

    def test_sampling_from_testobject_with_columns(
        self,
        backend,
    ):
        testobject = TestObjectDTO(
            name="core_account_payments",
            domain="payments",
            stage="test",
            instance="alpha",
        )
        primary_keys = ["id", "account_id"]
        key_sample = backend.get_sample_keys(
            query="""
                WITH __expected__ AS (
                SELECT *
                FROM payments_test.alpha.core_account_payments
                )
            """,
            primary_keys=primary_keys,
            sample_size=2,
            db=self.db,
        )
        columns = ["account_id", "customer_id"]
        sample = backend.get_sample_from_testobject(
            testobject=testobject,
            primary_keys=primary_keys,
            key_sample=key_sample,
            columns=columns,
        )
        assert list(sample.columns) == (columns + ["__concat_key__"])

    def test_sampling_from_query_fails_with_empty_keys(self, backend, test_query):
        with pytest.raises(DemoBackendError) as err:
            backend.get_sample_from_query(
                query=test_query,
                primary_keys=[],
                key_sample=["some_key"],
                db=self.db,
            )
        assert "non-empty" in str(err)

    def test_sampling_from_testobject_fails_for_files(self, backend):
        testobject = TestObjectDTO(
            name="raw_accounts",
            domain="payments",
            stage="test",
            instance="alpha",
        )
        with pytest.raises(DemoBackendError) as err:
            backend.get_sample_from_testobject(
                testobject=testobject,
                primary_keys=["id"],
                key_sample=["1"],
            )
        assert "Sampling files not yet supported" in str(err)

    def test_translate_query_resolves_table_names(self, backend):
        query = "SELECT * FROM stage_accounts"
        result = backend.translate_query(query=query, db=self.db)
        assert result == ("SELECT * FROM payments_test.alpha.stage_accounts")

    def test_translate_query_skips_already_qualified(self, backend):
        query = "SELECT * FROM payments_test.alpha.stage_accounts"
        result = backend.translate_query(query=query, db=self.db)
        assert result == query

    def test_run_query_returns_dataframe(self, backend):

        query = "SELECT * FROM payments_test.alpha.stage_accounts LIMIT 3"
        result = backend.run_query(query=query, db=self.db)
        assert isinstance(result, pl.DataFrame)
        assert len(result) == 3

    def test_get_raw_testobject(self, backend):
        testobject = TestObjectDTO(
            name="stage_accounts",
            domain="payments",
            stage="test",
            instance="alpha",
        )
        raw = backend.get_raw_testobject(testobject=testobject)
        assert raw.name == "raw_accounts"
        assert raw.domain == testobject.domain


class TestGetTestobjectRowcount:
    db = DBInstanceDTO(domain="payments", stage="test", instance="alpha")

    def test_db_rowcount_stage_accounts(self, backend):
        testobject = TestObjectDTO(
            name="stage_accounts", domain="payments", stage="test", instance="alpha"
        )
        count = backend.get_testobject_rowcount(testobject=testobject)
        assert count == 410  # 200 + 210

    def test_db_rowcount_stage_transactions(self, backend):
        testobject = TestObjectDTO(
            name="stage_transactions", domain="payments", stage="test", instance="alpha"
        )
        count = backend.get_testobject_rowcount(testobject=testobject)
        assert count == 1500  # 1000 + 500 (truncated)

    def test_db_rowcount_with_filter(self, backend):
        testobject = TestObjectDTO(
            name="stage_accounts", domain="payments", stage="test", instance="alpha"
        )
        count = backend.get_testobject_rowcount(
            testobject=testobject,
            filters=[("m__source_file", "='accounts_2024-01-01.csv'")],
        )
        assert count == 200

    def test_file_rowcount_returns_correct_count(self, backend, demo_data):
        testobject = TestObjectDTO(
            name="raw_accounts", domain="payments", stage="test", instance="alpha"
        )
        filepath = (
            f"{demo_data.raw_path}/payments/test/alpha/accounts/accounts_2024-01-01.csv"
        )
        count = backend.get_testobject_rowcount(
            testobject=testobject,
            filters=[("filepath", f"={filepath}")],
        )
        assert count == 200

    def test_file_rowcount_raises_without_filepath(self, backend):
        testobject = TestObjectDTO(
            name="raw_accounts", domain="payments", stage="test", instance="alpha"
        )
        with pytest.raises(DemoBackendError) as err:
            backend.get_testobject_rowcount(testobject=testobject)
        assert "filepath filter is required" in str(err)


class TestHarmonizeSchemaExtended:
    def _make_schema(self, columns: dict) -> SchemaSpecDTO:
        return SchemaSpecDTO(
            location=LocationDTO(path="duckdb://test.schema.table.duck"),
            columns=columns,
            testobject="test_table",
            spec_type=SpecType.SCHEMA,
        )

    def test_harmonize_float_dtypes(self, backend):
        schema = self._make_schema({"a": "FLOAT", "b": "REAL", "c": "DOUBLE"})
        result = backend.harmonize_schema(schema)
        assert result.columns == {"a": "float", "b": "float", "c": "float"}

    def test_harmonize_decimal_dtypes(self, backend):
        schema = self._make_schema({"a": "DECIMAL(10,2)", "b": "NUMERIC"})
        result = backend.harmonize_schema(schema)
        assert result.columns == {"a": "decimal", "b": "decimal"}

    def test_harmonize_date_dtype(self, backend):
        schema = self._make_schema({"a": "DATE"})
        result = backend.harmonize_schema(schema)
        assert result.columns == {"a": "date"}

    def test_harmonize_timestamp_dtype(self, backend):
        schema = self._make_schema({"a": "TIMESTAMP", "b": "TIMESTAMP WITH TIME ZONE"})
        result = backend.harmonize_schema(schema)
        assert result.columns == {"a": "timestamp", "b": "timestamp"}

    def test_harmonize_complex_dtypes_passthrough(self, backend):
        schema = self._make_schema(
            {
                "a": "ARRAY<STRING>",
                "b": "LIST(INTEGER)",
                "c": "INTERVAL",
                "d": "STRUCT(x INTEGER, y VARCHAR)",
            }
        )
        result = backend.harmonize_schema(schema)
        assert result.columns == {
            "a": "array<string>",
            "b": "list(integer)",
            "c": "interval",
            "d": "struct(x integer, y varchar)",
        }
