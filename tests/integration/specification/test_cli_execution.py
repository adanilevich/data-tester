import pytest
import io
from datetime import datetime
from uuid import uuid4
from typing import List, cast
import polars as pl

from src.drivers.cli.specification import CliSpecManager
from src.drivers.cli.specification_di import SpecDependencyInjector
from src.domain.specification.application.handle_specs import SpecCommandHandler
from src.config import Config
from src.dtos import (
    LocationDTO,
    TestCaseEntryDTO,
    TestSetDTO,
    TestType,
    SpecificationType,
    SchemaSpecificationDTO,
    RowCountSqlDTO,
)
from src.infrastructure.storage.i_storage import IStorage


@pytest.fixture
def config():
    """Create a Config instance for testing"""
    config = Config()
    config.DATATESTER_ENV = "LOCAL"
    config.DATATESTER_INTERNAL_STORAGE_ENGINE = "DICT"
    return config


@pytest.fixture
def spec_manager(config: Config) -> CliSpecManager:
    """Create a CliSpecManager instance with all dependencies injected"""
    injector = SpecDependencyInjector(config)
    manager = injector.cli_spec_manager()

    # Setup test data in the dict storage
    location = LocationDTO("dict://specs/")
    handler = cast(SpecCommandHandler, manager.spec_command_handler)
    storage = handler.storage_factory.get_storage(location)

    # Add test specification files
    _setup_test_specifications(storage)

    return manager


@pytest.fixture
def testset_dto() -> TestSetDTO:
    """Create a test TestSetDTO with various test cases"""
    testcases = {
        "customers_SCHEMA": TestCaseEntryDTO(
            testobject="customers",
            testtype=TestType.SCHEMA,
            comment="Schema test for customers table",
        ),
        "customers_ROWCOUNT": TestCaseEntryDTO(
            testobject="customers",
            testtype=TestType.ROWCOUNT,
            comment="Rowcount test for customers table",
        ),
        "orders_COMPARE": TestCaseEntryDTO(
            testobject="orders",
            testtype=TestType.COMPARE,
            comment="Compare sample test for orders table",
        ),
        "products_SCHEMA": TestCaseEntryDTO(
            testobject="products",
            testtype=TestType.SCHEMA,
            comment="Schema test for products table",
        ),
    }

    return TestSetDTO(
        testset_id=uuid4(),
        name="Integration Test Set",
        description="A test set for integration testing of specifications",
        labels=["integration-test", "specification"],
        domain="ecommerce",
        default_stage="test",
        default_instance="alpha",
        testcases=testcases,
        last_updated=datetime.now(),
    )


def _setup_test_specifications(storage: IStorage) -> None:
    """Setup test specification files in the dict storage"""
    # Create schema Excel files
    customers_schema = _create_test_xlsx_schema(
        columns=["customer_id", "name", "email", "created_at"],
        types=["INTEGER", "VARCHAR(255)", "VARCHAR(255)", "TIMESTAMP"],
        pk_flags=["x", "", "", ""],
        partition_flags=["", "", "", "x"],
        cluster_flags=["", "x", "", ""],
    )
    products_schema = _create_test_xlsx_schema(
        columns=["product_id", "name", "price", "category"],
        types=["INTEGER", "VARCHAR(100)", "DECIMAL(10,2)", "VARCHAR(50)"],
        pk_flags=["x", "", "", ""],
        partition_flags=["", "", "", "x"],
        cluster_flags=["", "", "", ""],
    )
    orders_schema = _create_test_xlsx_schema(
        columns=["order_id", "customer_id", "total", "order_date"],
        types=["INTEGER", "INTEGER", "DECIMAL(10,2)", "DATE"],
        pk_flags=["x", "", "", ""],
        partition_flags=["", "", "", "x"],
        cluster_flags=["", "", "", ""],
    )

    # Save schema files
    storage.write_bytes(
        customers_schema, LocationDTO("dict://specs/customers_schema.xlsx")
    )
    storage.write_bytes(products_schema, LocationDTO("dict://specs/products_schema.xlsx"))
    storage.write_bytes(orders_schema, LocationDTO("dict://specs/orders_schema.xlsx"))

    # Create and save rowcount SQL file
    rowcount_sql = (
        "SELECT COUNT(*) as __EXPECTED_ROWCOUNT__ FROM customers WHERE active = 1"
    )
    storage.write_bytes(
        rowcount_sql.encode(), LocationDTO("dict://specs/customers_ROWCOUNT.sql")
    )

    # Create and save compare SQL file
    compare_sql = """
    SELECT
        order_id,
        customer_id,
        total,
        order_date
    FROM orders
    WHERE order_date >= '2024-01-01'
    ORDER BY order_id
    LIMIT 100
    -- __EXPECTED__
    """
    storage.write_bytes(
        compare_sql.encode(), LocationDTO("dict://specs/orders_COMPARE.sql")
    )


def _create_test_xlsx_schema(
    columns: List[str],
    types: List[str],
    pk_flags: List[str],
    partition_flags: List[str],
    cluster_flags: List[str],
) -> bytes:
    """Create a test Excel file with schema data"""
    data = {
        "column": columns,
        "type": types,
        "pk": pk_flags,
        "partition": partition_flags,
        "cluster": cluster_flags,
    }
    df = pl.DataFrame(data)

    # Write to in-memory Excel file
    buffer = io.BytesIO()
    df.write_excel(buffer, worksheet="schema")
    return buffer.getvalue()


class TestCliSpecManagerE2E:
    """End-to-end integration tests for CliSpecManager"""

    def test_find_specifications_single_testcase(
        self, spec_manager: CliSpecManager, testset_dto: TestSetDTO
    ):
        """Test finding specifications for a single testcase"""
        # Given a testset with only one testcase
        single_testcase_testset = TestSetDTO(
            testset_id=testset_dto.testset_id,
            name=testset_dto.name,
            domain=testset_dto.domain,
            default_stage=testset_dto.default_stage,
            default_instance=testset_dto.default_instance,
            testcases={"customers_SCHEMA": testset_dto.testcases["customers_SCHEMA"]},
        )

        locations = [LocationDTO("dict://specs/")]

        # When finding specifications
        result = spec_manager.find_specifications(single_testcase_testset, locations)

        # Then specifications are found correctly
        assert len(result) == 1  # One testcase
        assert len(result[0]) == 1  # One schema spec found
        assert isinstance(result[0][0], SchemaSpecificationDTO)
        assert result[0][0].testobject == "customers"
        assert "customer_id" in result[0][0].columns
        assert "email" in result[0][0].columns

    def test_find_specifications_multiple_testcases(
        self, spec_manager: CliSpecManager, testset_dto: TestSetDTO
    ):
        """Test finding specifications for multiple testcases"""
        locations = [LocationDTO("dict://specs/")]

        # When finding specifications for all testcases
        result = spec_manager.find_specifications(testset_dto, locations)

        # Then specifications are found for all testcases
        assert len(result) == 4  # Four testcases in testset_dto

        # Verify results for each testcase (order matches testcases.values())

        # First testcase: customers_SCHEMA
        assert len(result[0]) == 1
        assert isinstance(result[0][0], SchemaSpecificationDTO)
        assert result[0][0].testobject == "customers"

        # Second testcase: customers_ROWCOUNT
        assert len(result[1]) == 1
        assert isinstance(result[1][0], RowCountSqlDTO)
        assert result[1][0].testobject == "customers"

        # Third testcase: orders_COMPARE
        assert len(result[2]) == 2  # Should find both SQL and schema specs
        spec_types = [spec.spec_type for spec in result[2]]
        assert SpecificationType.COMPARE_SQL in spec_types
        assert SpecificationType.SCHEMA in spec_types

        # Fourth testcase: products_SCHEMA
        assert len(result[3]) == 1
        assert isinstance(result[3][0], SchemaSpecificationDTO)
        assert result[3][0].testobject == "products"

    def test_find_specifications_multiple_locations(
        self, spec_manager: CliSpecManager, testset_dto: TestSetDTO
    ):
        """Test finding specifications from multiple locations"""
        # Setup backup location with duplicate schema files
        backup_location = LocationDTO("dict://backup/")
        handler = cast(SpecCommandHandler, spec_manager.spec_command_handler)
        storage = handler.storage_factory.get_storage(backup_location)

        # Copy some specs to backup location
        customers_schema = _create_test_xlsx_schema(
            columns=["customer_id", "name", "email"],
            types=["INTEGER", "VARCHAR(255)", "VARCHAR(255)"],
            pk_flags=["x", "", ""],
            partition_flags=["", "", ""],
            cluster_flags=["", "x", ""],
        )
        storage.write_bytes(
            customers_schema, LocationDTO("dict://backup/customers_schema.xlsx")
        )

        # Given testset with single testcase and multiple locations
        single_testcase_testset = TestSetDTO(
            testset_id=testset_dto.testset_id,
            name=testset_dto.name,
            domain=testset_dto.domain,
            default_stage=testset_dto.default_stage,
            default_instance=testset_dto.default_instance,
            testcases={"customers_SCHEMA": testset_dto.testcases["customers_SCHEMA"]},
        )

        locations = [LocationDTO("dict://specs/"), LocationDTO("dict://backup/")]

        # When finding specifications
        result = spec_manager.find_specifications(single_testcase_testset, locations)

        # Then specifications are found from both locations
        assert len(result) == 1  # One testcase
        assert len(result[0]) == 2  # Two schema specs found (one from each location)
        assert all(isinstance(spec, SchemaSpecificationDTO) for spec in result[0])
        assert all(spec.testobject == "customers" for spec in result[0])

    def test_find_specifications_no_specs_found(self, spec_manager: CliSpecManager):
        """Test behavior when no specifications are found"""
        # Given a testset with testcase that has no corresponding specs
        testcase = TestCaseEntryDTO(
            testobject="nonexistent_table",
            testtype=TestType.SCHEMA,
            comment="Test for non-existent table",
        )

        testset = TestSetDTO(
            testset_id=uuid4(),
            name="Empty Test Set",
            domain="test_domain",
            default_stage="dev",
            default_instance="primary",
            testcases={"nonexistent_SCHEMA": testcase},
        )

        locations = [LocationDTO("dict://specs/")]

        # When finding specifications
        result = spec_manager.find_specifications(testset, locations)

        # Then empty results are returned
        assert len(result) == 1  # One testcase
        assert len(result[0]) == 0  # No specs found

    def test_find_specifications_preserves_testcase_order(
        self, spec_manager: CliSpecManager
    ):
        """Test that find_specifications preserves the order of testcases"""
        # Given a testset with specific testcase order
        testcases = {
            "z_customers": TestCaseEntryDTO(
                testobject="customers", testtype=TestType.SCHEMA
            ),
            "a_products": TestCaseEntryDTO(
                testobject="products", testtype=TestType.SCHEMA
            ),
            "m_customers": TestCaseEntryDTO(
                testobject="customers", testtype=TestType.ROWCOUNT
            ),
        }

        testset = TestSetDTO(
            testset_id=uuid4(),
            name="Ordered Test Set",
            domain="ecommerce",
            default_stage="test",
            default_instance="alpha",
            testcases=testcases,
        )

        locations = [LocationDTO("dict://specs/")]

        # When finding specifications
        result = spec_manager.find_specifications(testset, locations)

        # Then results are returned in same order as testcases.values()
        assert len(result) == 3

        # Verify order matches the iteration order of testcases.values()
        testcase_list = list(testset.testcases.values())
        for i, testcase_specs in enumerate(result):
            expected_testcase = testcase_list[i]
            if len(testcase_specs) > 0:
                # Check that specs belong to the expected testcase
                assert all(
                    spec.testobject == expected_testcase.testobject
                    for spec in testcase_specs
                )

    def test_find_specifications_complex_scenario(
        self, spec_manager: CliSpecManager, testset_dto: TestSetDTO
    ):
        """Test complex scenario with multiple testcases, types, and locations"""
        # Setup additional location with some overlapping specs
        extra_location = LocationDTO("dict://extra/")
        handler = cast(SpecCommandHandler, spec_manager.spec_command_handler)
        storage = handler.storage_factory.get_storage(extra_location)

        # Add an additional rowcount spec for products
        products_rowcount_sql = (
            "SELECT COUNT(*) as __EXPECTED_ROWCOUNT__ FROM products WHERE active = 1"
        )
        storage.write_bytes(
            products_rowcount_sql.encode(),
            LocationDTO("dict://extra/products_ROWCOUNT.sql"),
        )

        locations = [LocationDTO("dict://specs/"), LocationDTO("dict://extra/")]

        # When finding specifications
        result = spec_manager.find_specifications(testset_dto, locations)

        # Then all specifications are found correctly
        assert len(result) == 4  # Four testcases

        # Verify that some testcases have specs from multiple locations
        total_specs_found = sum(len(specs) for specs in result)
        assert total_specs_found >= 5  # At least 5 specs should be found

        # Verify specific expectations for each testcase
        testcase_names = list(testset_dto.testcases.keys())

        # customers_SCHEMA should have schema spec
        customers_schema_idx = testcase_names.index("customers_SCHEMA")
        assert len(result[customers_schema_idx]) >= 1
        assert any(
            isinstance(spec, SchemaSpecificationDTO)
            for spec in result[customers_schema_idx]
        )

        # customers_ROWCOUNT should have rowcount spec
        customers_rowcount_idx = testcase_names.index("customers_ROWCOUNT")
        assert len(result[customers_rowcount_idx]) >= 1
        assert any(
            isinstance(spec, RowCountSqlDTO) for spec in result[customers_rowcount_idx]
        )
