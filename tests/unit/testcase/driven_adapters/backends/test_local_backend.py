import pytest

from src.testcase.adapters.backends import LocalBackendFactory
from src.dtos.testcase import DBInstanceDTO, TestObjectDTO


class TestLocalBackendFactory:

    def test_backend_creation(self, domain_config, prepare_local_data):
        factory = LocalBackendFactory()
        backend = factory.create(domain_config=domain_config)

        assert backend.config == domain_config


class TestLocalBackend:

    @pytest.fixture
    def test_query(self):
        query = """
            WITH __expected__ AS (
            SELECT * FROM payments_test.alpha.core_customer_transactions
            )
        """
        return query

    @pytest.fixture
    def backend(domain_config, prepare_local_data):
        return LocalBackendFactory().create(domain_config=domain_config)

    @pytest.mark.parametrize("domain,stage,instance,testobjects_expected", [
        ("payments", "uat", "main", ["stage_customers", "raw_customers"]),
        ("sales", "test", "main", ["stage_customers", "raw_customers"]),
        ("payments", "test", "alpha", [
            "stage_customers", "raw_customers", "stage_transactions", "raw_transactions",
            "core_customer_transactions"
        ]),
    ])
    def test_getting_testobjects(self, backend, domain, stage, instance,
                                 testobjects_expected):
        db = DBInstanceDTO(domain, stage, instance)

        testobjects_obtained = backend.get_testobjects(db)

        assert set(testobjects_obtained) == set(testobjects_expected)

    def test_getting_schema_of_file_objects_fails(self, backend):
        testobject = TestObjectDTO("raw_customers", "payments", "uat", "main")

        with pytest.raises(ValueError) as err:
            _ = backend.get_schema(testobject)

        assert "Getting schema for file-like testobjects" in str(err)

    def test_getting_schema_of_db_objects(self, backend):
        testobject = TestObjectDTO("stage_customers", "payments", "test", "alpha")

        schema = backend.get_schema(testobject)

        assert schema.columns == {
            "date": "VARCHAR", "id": "INTEGER", "region": "VARCHAR", "type": "VARCHAR",
            "name": "VARCHAR", "source_file": "VARCHAR"
        }
        assert schema.primary_keys is None
        assert schema.partition_columns is None
        assert schema.clustering_columns is None

    def test_getting_harmonized_schema_of_db_objects(self, backend):
        testobject = TestObjectDTO("stage_customers", "payments", "test", "alpha")

        schema = backend.get_schema(testobject)
        harmonized_schema = backend.harmonize_schema(schema)
        harmonized_schema.columns.update({"complex": "array<string>"})

        assert harmonized_schema.columns == {
            "date": "string", "id": "int", "region": "string", "type": "string",
            "name": "string", "source_file": "string", "complex": "array<string>"
        }

    def test_getting_sample_keys_fails_without_defining_pks(self, backend, test_query):

        primary_keys = []

        with pytest.raises(ValueError) as err:
            _ = backend.get_sample_keys(
                query=test_query, primary_keys=primary_keys, sample_size=5)

        assert "Provide a non-empty list of primary keys" in str(err)

    def test_that_unique_keys_are_sampled(self, backend,test_query):

        primary_keys = ["id"]

        key_sample = backend.get_sample_keys(
                query=test_query, primary_keys=primary_keys, sample_size=5)

        # primary keys are exact, so sample size must be equal specified size
        assert len(key_sample) == 5
        # all sampled key values must be unique
        assert len(set(key_sample)) == 5

    def test_sampling_with_underspecified_keys_works(self, backend, test_query):

        primary_keys = ["customer_name", "customer_id"]

        key_sample = backend.get_sample_keys(
                query=test_query, primary_keys=primary_keys, sample_size=2)

        # even for underspecified keys, key sample size must be exact
        assert len(key_sample) == 2
        # also all keys must be concatenations of columns defined in primary_keys
        for concat_key in key_sample:
            assert len(concat_key.split("|")) == 2

    def test_sampling_from_query_using_unique_keys(self, backend, test_query):

        primary_keys = ["customer_name", "id"]
        key_sample = ["Peter Lustig|1", "Big Company Ltd|5", "Big Company Ltd|1"]

        sample = backend.get_sample_from_query(
            query=test_query, primary_keys=primary_keys, key_sample=key_sample)

        assert sum(sample["amount"]) == 3010

    def test_sampling_from_query_using_non_unique_keys(self, backend, test_query):

        primary_keys = ["customer_name"]
        key_sample = ["Peter Lustig"]

        sample = backend.get_sample_from_query(
            query=test_query, primary_keys=primary_keys, key_sample=key_sample)

        assert sum(sample["amount"]) == 21

    def test_sampling_from_testobject_using_unique_keys(self, backend):
        testobject = TestObjectDTO(
            "core_customer_transactions", "payments", "test", "alpha")
        primary_keys = ["customer_name", "id"]
        key_sample = ["Peter Lustig|1", "Big Company Ltd|5", "Big Company Ltd|1"]

        sample = backend.get_sample_from_testobject(
            testobject=testobject, primary_keys=primary_keys, key_sample=key_sample)

        assert sum(sample["amount"]) == 3010

    def test_sampling_from_testobject_using_non_unique_keys(self, backend):
        testobject = TestObjectDTO(
            "core_customer_transactions", "payments", "test", "alpha")
        primary_keys = ["customer_name"]
        key_sample = ["Peter Lustig"]

        sample = backend.get_sample_from_testobject(
            testobject=testobject, primary_keys=primary_keys, key_sample=key_sample)

        assert sum(sample["amount"]) == 21

    def test_sampling_from_testobject_using_column_filters(self, backend):
        testobject = TestObjectDTO(
            "core_customer_transactions", "payments", "test", "alpha")
        primary_keys = ["customer_name"]
        key_sample = ["Peter Lustig"]
        columns = ["customer_name", "customer_id"]

        sample = backend.get_sample_from_testobject(
            testobject=testobject,
            primary_keys=primary_keys,
            key_sample=key_sample,
            columns=columns
        )

        assert list(sample.keys()) == columns + ["__concat_key__"]
