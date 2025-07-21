import pytest
import io
from unittest.mock import Mock, patch

from src.specification.core.specification import Specification
from src.specification.adapters.naming_conventions import NamingConventionsFactory
from src.specification.adapters.formatter import FormatterFactory
from src.specification.adapters.requirements import Requirements
from src.storage.dict_storage import DictStorage
from src.dtos import (
    LocationDTO,
    TestCaseEntryDTO,
    TestType,
    SpecificationType,
    SchemaSpecificationDTO,
    RowCountSqlDTO,
    CompareSqlDTO,
)


class TestSpecification:
    """Test suite for the Specification class"""

    @pytest.fixture
    def storage(self) -> DictStorage:
        """Create a DictStorage instance with test data"""
        storage = DictStorage()

        # Add schema xlsx file for table1
        schema_data = self._create_test_xlsx_schema()
        storage.write(schema_data, LocationDTO("dict://specs/table1_schema.xlsx"))

        # Add rowcount SQL file for table1
        rowcount_sql = "SELECT COUNT(*) as __EXPECTED_ROWCOUNT__ FROM table1"
        storage.write(
            rowcount_sql.encode(), LocationDTO("dict://specs/table1_ROWCOUNT.sql")
        )

        # Add compare sample SQL file for table2
        compare_sql = "SELECT id, name FROM table2 WHERE id = 1 -- __EXPECTED__"
        storage.write(
            compare_sql.encode(), LocationDTO("dict://specs/table2_COMPARE.sql")
        )

        # Add schema file for table2 (for COMPARE which needs both)
        storage.write(schema_data, LocationDTO("dict://specs/table2_schema.xlsx"))

        return storage

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
    def specification(
        self,
        storage: DictStorage,
        naming_conventions_factory: NamingConventionsFactory,
        formatter_factory: FormatterFactory,
        requirements: Requirements,
    ) -> Specification:
        """Create a Specification instance with all dependencies"""
        return Specification(
            storage=storage,
            naming_conventions_factory=naming_conventions_factory,
            formatter_factory=formatter_factory,
            requirements=requirements,
        )

    def _create_test_xlsx_schema(self) -> bytes:
        """Create a test Excel file with schema data"""
        import polars as pl

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

    def test_init(self, specification: Specification):
        """Test that Specification initializes correctly"""
        assert specification.storage is not None
        assert specification.naming_conventions_factory is not None
        assert specification.formatter_factory is not None
        assert specification.requirements is not None

    def test_find_specs_schema(self, specification: Specification):
        """Test find_specs for schema test type"""
        location = LocationDTO("dict://specs/")
        testcase = TestCaseEntryDTO(testobject="table1", testtype=TestType.SCHEMA)

        specs = specification.find_specs(location, testcase, "test_domain")

        assert len(specs) == 1
        assert isinstance(specs[0], SchemaSpecificationDTO)
        assert specs[0].testobject == "table1"
        assert specs[0].spec_type == SpecificationType.SCHEMA
        assert "id" in specs[0].columns
        assert "name" in specs[0].columns
        assert "created_at" in specs[0].columns

    def test_find_specs_rowcount(self, specification: Specification):
        """Test find_specs for rowcount test type"""
        location = LocationDTO("dict://specs/")
        testcase = TestCaseEntryDTO(testobject="table1", testtype=TestType.ROWCOUNT)

        specs = specification.find_specs(location, testcase, "test_domain")

        assert len(specs) == 1
        assert isinstance(specs[0], RowCountSqlDTO)
        assert specs[0].testobject == "table1"
        assert specs[0].spec_type == SpecificationType.ROWCOUNT_SQL
        assert "__EXPECTED_ROWCOUNT__" in specs[0].query

    def test_find_specs_compare(self, specification: Specification):
        """Test find_specs for compare sample test type (requires both SQL and schema)"""
        location = LocationDTO("dict://specs/")
        testcase = TestCaseEntryDTO(testobject="table2", testtype=TestType.COMPARE)

        specs = specification.find_specs(location, testcase, "test_domain")

        # Should find compare SQL and also the schema definition file
        assert len(specs) == 2
        assert specs[0].spec_type == SpecificationType.COMPARE_SQL
        assert specs[1].spec_type == SpecificationType.SCHEMA

    def test_find_specs_no_matching_files(self, specification: Specification):
        """Test find_specs when no matching files are found"""
        location = LocationDTO("dict://specs/")
        testcase = TestCaseEntryDTO(testobject="nonexistent", testtype=TestType.SCHEMA)

        specs = specification.find_specs(location, testcase, "test_domain")

        assert len(specs) == 0

    def test_find_specs_handles_parsing_errors(self, specification: Specification):
        """Test that find_specs gracefully handles parsing errors"""
        from unittest.mock import patch

        location = LocationDTO("dict://specs/")
        testcase = TestCaseEntryDTO(testobject="table1", testtype=TestType.SCHEMA)

        # Mock formatter to raise an exception during deserialization
        mock_formatter = Mock()
        mock_formatter.deserialize.side_effect = Exception("Parse error")

        with patch.object(
            specification.formatter_factory, 'get_formatter', return_value=mock_formatter
        ):
            specs = specification.find_specs(location, testcase, "test_domain")
            # Should return empty list when parsing fails
            assert len(specs) == 0

    def test_find_specs_with_unsupported_test_type(self, specification: Specification):
        """Test find_specs with an unsupported test type"""
        location = LocationDTO("dict://specs/")
        # Unsupported type
        testcase = TestCaseEntryDTO(testobject="table1", testtype=TestType.DUMMY_OK)

        with pytest.raises(ValueError):
            specification.find_specs(location, testcase, "test_domain")

    def test_parse_spec_file_schema(self, specification: Specification):
        """Test parse_spec_file with a schema Excel file"""
        schema_data = self._create_test_xlsx_schema()

        specs = specification.parse_spec_file(schema_data, "test_table")

        # Should successfully parse one schema specification
        assert len(specs) == 1
        assert isinstance(specs[0], SchemaSpecificationDTO)
        assert specs[0].testobject == "test_table"
        assert specs[0].location.path == "upload://test_table_schema.file"

    def test_parse_spec_file_rowcount_sql(self, specification: Specification):
        """Test parse_spec_file with rowcount SQL content"""
        sql_content = "SELECT COUNT(*) as __EXPECTED_ROWCOUNT__ FROM table1".encode()

        specs = specification.parse_spec_file(sql_content, "test_table")

        assert len(specs) == 1
        assert isinstance(specs[0], RowCountSqlDTO)
        assert specs[0].testobject == "test_table"
        assert specs[0].location.path == "upload://test_table_rowcount_sql.file"

    def test_parse_spec_file_compare_sql(self, specification: Specification):
        """Test parse_spec_file with compare SQL content"""
        sql_content = "SELECT * FROM table1 -- __EXPECTED__".encode()

        specs = specification.parse_spec_file(sql_content, "test_table")

        assert len(specs) == 1
        assert isinstance(specs[0], CompareSqlDTO)
        assert specs[0].testobject == "test_table"
        assert specs[0].location.path == "upload://test_table_compare_sql.file"

    def test_parse_spec_file_invalid_content(self, specification: Specification):
        """Test parse_spec_file with invalid content that can't be parsed"""
        invalid_content = b"invalid content"

        specs = specification.parse_spec_file(invalid_content, "test_table")

        # Should return empty list when no parsers succeed
        assert len(specs) == 0

    def test_find_specs_handles_file_read_errors(self, specification: Specification):
        """Test that find_specs gracefully handles file read errors"""

        location = LocationDTO("dict://specs/")
        testcase = TestCaseEntryDTO(testobject="table1", testtype=TestType.SCHEMA)

        # Mock storage.read to raise an exception
        with patch.object(
            specification.storage, 'read', side_effect=Exception("Read error")
        ):
            specs = specification.find_specs(location, testcase, "test_domain")
            # Should return empty list when files can't be read
            assert len(specs) == 0

    def test_find_specs_partial_success(
        self, specification: Specification, storage: DictStorage
    ):
        """Test find_specs when some files parse successfully and others fail"""
        # Add a corrupted Excel file that will fail to parse
        storage.write(
            b"corrupted excel data", LocationDTO("dict://specs/table3_schema.xlsx"))

        # Also add a valid SQL file for same testobject
        sql_content = "SELECT COUNT(*) as __EXPECTED_ROWCOUNT__ FROM table3"
        storage.write(
            sql_content.encode(), LocationDTO("dict://specs/table3_ROWCOUNT.sql"))

        location = LocationDTO("dict://specs/")
        testcase = TestCaseEntryDTO(testobject="table3", testtype=TestType.COMPARE)

        specs = specification.find_specs(location, testcase, "test_domain")

        # Should only return successfully parsed specs, ignoring failed ones
        # COMPARE requires both COMPARE_SQL and SCHEMA,
        # but we only have corrupted schema
        # So we should get 0 specs since schema parsing fails
        assert len(specs) == 0
