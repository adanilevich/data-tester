import pytest

from src.testcase.adapters.backends import LocalBackendFactory


class TestLocalBackendFactory:

    def test_backend_creation(self, domain_config, prepare_local_data):
        factory = LocalBackendFactory()
        backend = factory.create(domain_config=domain_config)

        assert backend.config == domain_config


@pytest.fixture
def local_backend(domain_config, prepare_local_data):
    return LocalBackendFactory().create(domain_config=domain_config)


class TestLocalBackend:

    @pytest.mark.parametrize("domain,stage,instance,testobjects_expected", [
        ("payments", "uat", "main", ["stage_customers", "raw_customers"]),
        ("sales", "test", "main", ["stage_customers", "raw_customers"]),
        ("payments", "test", "alpha", [
            "stage_customers", "raw_customers", "stage_transactions", "raw_transactions",
            "core_customer_transactions"
        ]),
    ])
    def test_getting_testobjects(self, local_backend, domain, stage, instance,
                                 testobjects_expected):
        testobjects_obtained = local_backend.get_testobjects(domain, stage, instance)

        assert set(testobjects_obtained) == set(testobjects_expected)

    def test_getting_schema_of_file_objects_fails(self, local_backend):
        with pytest.raises(ValueError) as err:
            _ = local_backend.get_schema("payments", "uat", "main", "raw_customers")
        assert "Getting schema for file-like testobjects" in str(err)

    def test_getting_schema_of_db_objects(self, local_backend):
        schema = local_backend.get_schema(
            "payments", "test", "alpha", "stage_customers")
        assert schema.columns == {
            "date": "VARCHAR", "id": "INTEGER", "region": "VARCHAR", "type": "VARCHAR",
            "name": "VARCHAR", "source_file": "VARCHAR"
        }
        assert schema.primary_keys is None
        assert schema.partition_columns is None
        assert schema.clustering_columns is None

    def test_getting_harmonized_schema_of_db_objects(self, local_backend):
        schema = local_backend.get_schema(
            "payments", "test", "alpha", "stage_customers")
        harmonized_schema = local_backend.harmonize_schema(schema)
        harmonized_schema.columns.update({"complex": "array<string>"})
        assert harmonized_schema.columns == {
            "date": "string", "id": "int", "region": "string", "type": "string",
            "name": "string", "source_file": "string", "complex": "array<string>"
        }
