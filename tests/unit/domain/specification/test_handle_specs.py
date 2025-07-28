import pytest
import io
from datetime import datetime
from uuid import uuid4
from typing import cast
import polars as pl

from src.domain.specification.application.handle_specs import SpecCommandHandler
from src.domain.specification.plugins.naming_conventions import NamingConventionsFactory
from src.domain.specification.plugins.formatter import FormatterFactory
from src.domain.specification.plugins.requirements import Requirements
from src.infrastructure.storage.dict_storage import DictStorage
from src.infrastructure.storage.formatter_factory import (
    FormatterFactory as StorageFormatterFactory,
)
from src.infrastructure.storage.storage_factory import StorageFactory
from src.config import Config
from src.domain.specification.ports.drivers.i_handle_specs import (
    FetchSpecsCommand,
    ParseSpecCommand,
)
from src.dtos import (
    LocationDTO,
    TestCaseEntryDTO,
    TestSetDTO,
    TestType,
    SpecificationType,
    SchemaSpecificationDTO,
    RowCountSqlDTO,
)


class TestSpecCommandHandler:
    """Test suite for the SpecCommandHandler class"""

    @pytest.fixture
    def storage_factory(self) -> StorageFactory:
        """Create a StorageFactory instance"""
        config = Config()
        storage_formatter_factory = StorageFormatterFactory()
        storage_factory = StorageFactory(config, storage_formatter_factory)

        """Create a DictStorage instance with test data"""
        location = LocationDTO("dict://specs/")
        storage = cast(DictStorage, storage_factory.get_storage(location))

        # Add schema xlsx file for table1
        schema_data = self._create_test_xlsx_schema()
        storage.write_bytes(schema_data, LocationDTO("dict://specs/table1_schema.xlsx"))
        storage.write_bytes(schema_data, LocationDTO("dict://backup/table1_schema.xlsx"))

        # Add rowcount SQL file for table1
        rowcount_sql = "SELECT COUNT(*) as __EXPECTED_ROWCOUNT__ FROM table1"
        storage.write_bytes(
            rowcount_sql.encode(), LocationDTO("dict://specs/table1_ROWCOUNT.sql")
        )

        # Add compare sample SQL and schema files for table2
        compare_sql = "SELECT id, name FROM table2 WHERE id = 1 -- __EXPECTED__"
        storage.write_bytes(
            compare_sql.encode(), LocationDTO("dict://specs/table2_COMPARE.sql")
        )
        storage.write_bytes(schema_data, LocationDTO("dict://specs/table2_schema.xlsx"))

        return storage_factory

    @pytest.fixture
    def naming_conventions_factory(self) -> NamingConventionsFactory:
        """Create a NamingConventionsFactory instance"""
        return NamingConventionsFactory()

    @pytest.fixture
    def formatter_factory(self) -> FormatterFactory:
        """Create a FormatterFactory instance"""
        return FormatterFactory()

    @pytest.fixture
    def requirements(self) -> Requirements:
        """Create a Requirements instance"""
        return Requirements()

    @pytest.fixture
    def handler(
        self,
        storage_factory: StorageFactory,
        naming_conventions_factory: NamingConventionsFactory,
        formatter_factory: FormatterFactory,
        requirements: Requirements,
    ) -> SpecCommandHandler:
        """Create a SpecCommandHandler instance with all dependencies"""
        return SpecCommandHandler(
            naming_conventions_factory=naming_conventions_factory,
            storage_factory=storage_factory,
            formatter_factory=formatter_factory,
            requirements=requirements,
        )

    @pytest.fixture
    def test_testset(self) -> TestSetDTO:
        """Create a test TestSetDTO with various test cases"""
        testcases = {
            "table1_SCHEMA": TestCaseEntryDTO(
                testobject="table1",
                testtype=TestType.SCHEMA,
                comment="Schema test for table1",
            ),
            "table1_ROWCOUNT": TestCaseEntryDTO(
                testobject="table1",
                testtype=TestType.ROWCOUNT,
                comment="Rowcount test for table1",
            ),
            "table2_COMPARE": TestCaseEntryDTO(
                testobject="table2",
                testtype=TestType.COMPARE,
                comment="Compare sample test for table2",
            ),
        }

        return TestSetDTO(
            testset_id=uuid4(),
            name="Test TestSet",
            description="A test set for unit testing",
            labels=["unit-test", "specification"],
            domain="test_domain",
            default_stage="dev",
            default_instance="primary",
            testcases=testcases,
            last_updated=datetime.now(),
        )

    def _create_test_xlsx_schema(self) -> bytes:
        """Create a test Excel file with schema data"""

        # Create test data for schema
        data = {
            "column": ["id", "name", "created_at"],
            "type": ["INTEGER", "VARCHAR(255)", "TIMESTAMP"],
            "pk": ["x", "", ""],
            "partition": ["", "", "x"],
            "cluster": ["", "x", ""],
        }
        df = pl.DataFrame(data)

        # Write to in-memory Excel file
        buffer = io.BytesIO()
        df.write_excel(buffer, worksheet="schema")
        return buffer.getvalue()

    def test_init(self, handler: SpecCommandHandler):
        """Test that SpecCommandHandler initializes correctly"""
        assert handler.naming_conventions_factory is not None
        assert handler.storage_factory is not None
        assert handler.formatter_factory is not None
        assert handler.requirements is not None
        assert handler.spec_manager is not None

    def test_fetch_specs_single_location_single_testcase(
        self, handler: SpecCommandHandler, test_testset: TestSetDTO
    ):
        """Test fetch_specs with single location and single testcase"""
        # Create a testset with only one testcase
        single_testcase_testset = TestSetDTO(
            testset_id=test_testset.testset_id,
            name=test_testset.name,
            domain=test_testset.domain,
            default_stage=test_testset.default_stage,
            default_instance=test_testset.default_instance,
            testcases={"table1_SCHEMA": test_testset.testcases["table1_SCHEMA"]},
        )

        command = FetchSpecsCommand(
            locations=[LocationDTO("dict://specs/")],
            testset=single_testcase_testset,
        )

        result = handler.fetch_specs(command)

        # Should return list of lists, one for each testcase
        assert len(result) == 1
        assert len(result[0]) == 1  # One spec found for the testcase
        assert isinstance(result[0][0], SchemaSpecificationDTO)
        assert result[0][0].testobject == "table1"

    def test_fetch_specs_multiple_locations(
        self, handler: SpecCommandHandler, test_testset: TestSetDTO
    ):
        """Test fetch_specs with multiple locations"""
        # Create a testset with only one testcase for simplicity
        single_testcase_testset = TestSetDTO(
            testset_id=test_testset.testset_id,
            name=test_testset.name,
            domain=test_testset.domain,
            default_stage=test_testset.default_stage,
            default_instance=test_testset.default_instance,
            testcases={"table1_SCHEMA": test_testset.testcases["table1_SCHEMA"]},
        )

        command = FetchSpecsCommand(
            locations=[
                LocationDTO("dict://specs/"),
                LocationDTO("dict://backup/"),
            ],
            testset=single_testcase_testset,
        )

        result = handler.fetch_specs(command)

        # Should find specs in both locations
        assert len(result) == 1  # One testcase
        assert len(result[0]) == 2  # Two specs found (one from each location)
        assert all(isinstance(spec, SchemaSpecificationDTO) for spec in result[0])
        assert all(spec.testobject == "table1" for spec in result[0])

    def test_fetch_specs_multiple_testcases(
        self, handler: SpecCommandHandler, test_testset: TestSetDTO
    ):
        """Test fetch_specs with multiple testcases"""
        command = FetchSpecsCommand(
            locations=[LocationDTO("dict://specs/")],
            testset=test_testset,
        )

        result = handler.fetch_specs(command)

        # Should return specs for all testcases
        assert len(result) == 3  # Three testcases in test_testset

        # Check each testcase's specs
        # Results are in same order as testcases.values()

        # First testcase: table1_SCHEMA
        assert len(result[0]) == 1
        assert isinstance(result[0][0], SchemaSpecificationDTO)
        assert result[0][0].testobject == "table1"

        # Second testcase: table1_ROWCOUNT
        assert len(result[1]) == 1
        assert isinstance(result[1][0], RowCountSqlDTO)
        assert result[1][0].testobject == "table1"

        # Third testcase: table2_COMPARE
        assert len(result[2]) == 2  # Should find both SQL and schema specs
        spec_types = [spec.spec_type for spec in result[2]]
        assert SpecificationType.COMPARE_SQL in spec_types
        assert SpecificationType.SCHEMA in spec_types

    def test_fetch_specs_no_specs_found(self, handler: SpecCommandHandler):
        """Test fetch_specs when no specifications are found"""
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

        command = FetchSpecsCommand(
            locations=[LocationDTO("dict://specs/")],
            testset=testset,
        )

        result = handler.fetch_specs(command)

        # Should return empty list for the testcase
        assert len(result) == 1
        assert len(result[0]) == 0

    def test_parse_spec_schema_file(self, handler: SpecCommandHandler):
        """Test parse_spec with schema Excel file"""
        schema_data = self._create_test_xlsx_schema()

        command = ParseSpecCommand(file=schema_data, testobject="test_table")

        result = handler.parse_spec(command)

        # Should successfully parse as schema
        schema_specs = [s for s in result if s.spec_type == SpecificationType.SCHEMA]
        assert len(schema_specs) == 1
        assert isinstance(schema_specs[0], SchemaSpecificationDTO)
        assert schema_specs[0].testobject == "test_table"
        assert "id" in schema_specs[0].columns
        assert "name" in schema_specs[0].columns

    def test_fetch_specs_preserves_testcase_order(self, handler: SpecCommandHandler):
        """Test that fetch_specs preserves the order of testcases"""
        # Create testset with specific order
        testcases = {
            "z_table": TestCaseEntryDTO(testobject="table1", testtype=TestType.SCHEMA),
            "a_table": TestCaseEntryDTO(testobject="table2", testtype=TestType.SCHEMA),
            "m_table": TestCaseEntryDTO(testobject="table1", testtype=TestType.ROWCOUNT),
        }

        testset = TestSetDTO(
            testset_id=uuid4(),
            name="Ordered Test Set",
            domain="test_domain",
            default_stage="dev",
            default_instance="primary",
            testcases=testcases,
        )

        command = FetchSpecsCommand(
            locations=[LocationDTO("dict://specs/")],
            testset=testset,
        )

        result = handler.fetch_specs(command)

        # Should return results in same order as testcases.values()
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
