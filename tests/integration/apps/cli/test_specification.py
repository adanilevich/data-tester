import pytest
import io
from datetime import datetime
from uuid import uuid4
from typing import List, cast
import polars as pl

from src.apps.cli_di import CliDependencyInjector
from src.drivers import SpecDriver
from src.domain import SpecAdapter
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
from src.infrastructure.storage.user_storage import (
    MemoryUserStorage,
)


def _put(
    storage: MemoryUserStorage, path: str, data: bytes
) -> None:
    """Write test data into MemoryUserStorage."""
    with storage.fs.open(path, mode="wb") as f:
        f.write(data)


@pytest.fixture
def config():
    """Create a Config instance for testing"""
    config = Config()
    config.DATATESTER_ENV = "LOCAL"
    return config


@pytest.fixture
def spec_manager(config: Config) -> SpecDriver:
    """Create a CliSpecManager instance with all
    dependencies injected"""
    injector = CliDependencyInjector(config)
    manager = injector.specification_driver()

    # Setup test data in the memory user storage
    handler = cast(
        SpecAdapter, manager.spec_command_handler
    )
    storage = cast(
        MemoryUserStorage, handler.user_storage
    )

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
        description="A test set for integration testing",
        labels=["integration-test", "specification"],
        domain="ecommerce",
        default_stage="test",
        default_instance="alpha",
        testcases=testcases,
        last_updated=datetime.now(),
    )


def _setup_test_specifications(
    storage: MemoryUserStorage,
) -> None:
    """Setup test specification files in memory storage"""
    customers_schema = _create_test_xlsx_schema(
        columns=[
            "customer_id",
            "name",
            "email",
            "created_at",
        ],
        types=[
            "INTEGER",
            "VARCHAR(255)",
            "VARCHAR(255)",
            "TIMESTAMP",
        ],
        pk_flags=["x", "", "", ""],
        partition_flags=["", "", "", "x"],
        cluster_flags=["", "x", "", ""],
    )
    products_schema = _create_test_xlsx_schema(
        columns=[
            "product_id",
            "name",
            "price",
            "category",
        ],
        types=[
            "INTEGER",
            "VARCHAR(100)",
            "DECIMAL(10,2)",
            "VARCHAR(50)",
        ],
        pk_flags=["x", "", "", ""],
        partition_flags=["", "", "", "x"],
        cluster_flags=["", "", "", ""],
    )
    orders_schema = _create_test_xlsx_schema(
        columns=[
            "order_id",
            "customer_id",
            "total",
            "order_date",
        ],
        types=[
            "INTEGER",
            "INTEGER",
            "DECIMAL(10,2)",
            "DATE",
        ],
        pk_flags=["x", "", "", ""],
        partition_flags=["", "", "", "x"],
        cluster_flags=["", "", "", ""],
    )

    _put(
        storage,
        "specs/customers_schema.xlsx",
        customers_schema,
    )
    _put(
        storage,
        "specs/products_schema.xlsx",
        products_schema,
    )
    _put(
        storage, "specs/orders_schema.xlsx", orders_schema
    )

    rowcount_sql = (
        "SELECT COUNT(*) as __EXPECTED_ROWCOUNT__ "
        "FROM customers WHERE active = 1"
    )
    _put(
        storage,
        "specs/customers_ROWCOUNT.sql",
        rowcount_sql.encode(),
    )

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
    _put(
        storage,
        "specs/orders_COMPARE.sql",
        compare_sql.encode(),
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

    buffer = io.BytesIO()
    df.write_excel(buffer, worksheet="schema")
    return buffer.getvalue()


class TestCliSpecManagerE2E:
    """End-to-end integration tests for CliSpecManager"""

    def test_find_specifications_single_testcase(
        self,
        spec_manager: SpecDriver,
        testset_dto: TestSetDTO,
    ):
        """Test finding specs for a single testcase"""
        single_testcase_testset = TestSetDTO(
            testset_id=testset_dto.testset_id,
            name=testset_dto.name,
            domain=testset_dto.domain,
            default_stage=testset_dto.default_stage,
            default_instance=testset_dto.default_instance,
            testcases={
                "customers_SCHEMA": testset_dto.testcases[
                    "customers_SCHEMA"
                ]
            },
        )

        locations = [LocationDTO("memory://specs/")]

        result = spec_manager.find_specifications(
            single_testcase_testset, locations
        )

        assert len(result) == 1
        assert len(result[0]) == 1
        assert isinstance(
            result[0][0], SchemaSpecificationDTO
        )
        assert result[0][0].testobject == "customers"
        assert "customer_id" in result[0][0].columns
        assert "email" in result[0][0].columns

    def test_find_specifications_multiple_testcases(
        self,
        spec_manager: SpecDriver,
        testset_dto: TestSetDTO,
    ):
        """Test finding specs for multiple testcases"""
        locations = [LocationDTO("memory://specs/")]

        result = spec_manager.find_specifications(
            testset_dto, locations
        )

        assert len(result) == 4

        # customers_SCHEMA
        assert len(result[0]) == 1
        assert isinstance(
            result[0][0], SchemaSpecificationDTO
        )
        assert result[0][0].testobject == "customers"

        # customers_ROWCOUNT
        assert len(result[1]) == 1
        assert isinstance(result[1][0], RowCountSqlDTO)
        assert result[1][0].testobject == "customers"

        # orders_COMPARE
        assert len(result[2]) == 2
        spec_types = [
            spec.spec_type for spec in result[2]
        ]
        assert SpecificationType.COMPARE_SQL in spec_types
        assert SpecificationType.SCHEMA in spec_types

        # products_SCHEMA
        assert len(result[3]) == 1
        assert isinstance(
            result[3][0], SchemaSpecificationDTO
        )
        assert result[3][0].testobject == "products"

    def test_find_specifications_multiple_locations(
        self,
        spec_manager: SpecDriver,
        testset_dto: TestSetDTO,
    ):
        """Test finding specs from multiple locations"""
        handler = cast(
            SpecAdapter,
            spec_manager.spec_command_handler,
        )
        storage = cast(
            MemoryUserStorage, handler.user_storage
        )

        customers_schema = _create_test_xlsx_schema(
            columns=["customer_id", "name", "email"],
            types=[
                "INTEGER",
                "VARCHAR(255)",
                "VARCHAR(255)",
            ],
            pk_flags=["x", "", ""],
            partition_flags=["", "", ""],
            cluster_flags=["", "x", ""],
        )
        _put(
            storage,
            "backup/customers_schema.xlsx",
            customers_schema,
        )

        single_testcase_testset = TestSetDTO(
            testset_id=testset_dto.testset_id,
            name=testset_dto.name,
            domain=testset_dto.domain,
            default_stage=testset_dto.default_stage,
            default_instance=testset_dto.default_instance,
            testcases={
                "customers_SCHEMA": testset_dto.testcases[
                    "customers_SCHEMA"
                ]
            },
        )

        locations = [
            LocationDTO("memory://specs/"),
            LocationDTO("memory://backup/"),
        ]

        result = spec_manager.find_specifications(
            single_testcase_testset, locations
        )

        assert len(result) == 1
        assert len(result[0]) == 2
        assert all(
            isinstance(spec, SchemaSpecificationDTO)
            for spec in result[0]
        )
        assert all(
            spec.testobject == "customers"
            for spec in result[0]
        )

    def test_find_specifications_no_specs_found(
        self, spec_manager: SpecDriver
    ):
        """Test when no specifications are found"""
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

        locations = [LocationDTO("memory://specs/")]

        result = spec_manager.find_specifications(
            testset, locations
        )

        assert len(result) == 1
        assert len(result[0]) == 0

    def test_find_specifications_preserves_testcase_order(
        self, spec_manager: SpecDriver
    ):
        """Test that find_specifications preserves order"""
        testcases = {
            "z_customers": TestCaseEntryDTO(
                testobject="customers",
                testtype=TestType.SCHEMA,
            ),
            "a_products": TestCaseEntryDTO(
                testobject="products",
                testtype=TestType.SCHEMA,
            ),
            "m_customers": TestCaseEntryDTO(
                testobject="customers",
                testtype=TestType.ROWCOUNT,
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

        locations = [LocationDTO("memory://specs/")]

        result = spec_manager.find_specifications(
            testset, locations
        )

        assert len(result) == 3

        testcase_list = list(testset.testcases.values())
        for i, testcase_specs in enumerate(result):
            expected_testcase = testcase_list[i]
            if len(testcase_specs) > 0:
                assert all(
                    spec.testobject
                    == expected_testcase.testobject
                    for spec in testcase_specs
                )

    def test_find_specifications_complex_scenario(
        self,
        spec_manager: SpecDriver,
        testset_dto: TestSetDTO,
    ):
        """Test complex scenario with multiple testcases,
        types, and locations"""
        handler = cast(
            SpecAdapter,
            spec_manager.spec_command_handler,
        )
        storage = cast(
            MemoryUserStorage, handler.user_storage
        )

        products_rowcount_sql = (
            "SELECT COUNT(*) as __EXPECTED_ROWCOUNT__ "
            "FROM products WHERE active = 1"
        )
        _put(
            storage,
            "extra/products_ROWCOUNT.sql",
            products_rowcount_sql.encode(),
        )

        locations = [
            LocationDTO("memory://specs/"),
            LocationDTO("memory://extra/"),
        ]

        result = spec_manager.find_specifications(
            testset_dto, locations
        )

        assert len(result) == 4

        total_specs_found = sum(
            len(specs) for specs in result
        )
        assert total_specs_found >= 5

        testcase_names = list(
            testset_dto.testcases.keys()
        )

        customers_schema_idx = testcase_names.index(
            "customers_SCHEMA"
        )
        assert len(result[customers_schema_idx]) >= 1
        assert any(
            isinstance(spec, SchemaSpecificationDTO)
            for spec in result[customers_schema_idx]
        )

        customers_rowcount_idx = testcase_names.index(
            "customers_ROWCOUNT"
        )
        assert len(result[customers_rowcount_idx]) >= 1
        assert any(
            isinstance(spec, RowCountSqlDTO)
            for spec in result[customers_rowcount_idx]
        )
