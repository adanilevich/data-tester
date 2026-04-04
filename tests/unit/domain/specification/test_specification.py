import io
from unittest.mock import Mock, patch

import pytest
import polars as pl

from src.domain.specification import Specification
from src.domain.specification.plugins import (
    NamingConventionsFactory,
    SpecParserFactory,
    SpecNamingConventionsError,
)
from src.infrastructure_ports import StorageError
from src.infrastructure.storage.user_storage import (
    MemoryUserStorage,
)
from src.dtos import (
    LocationDTO,
    TestCaseEntryDTO,
    TestType,
    SpecType,
    SchemaSpecDTO,
    RowcountSpecDTO,
    CompareSpecDTO,
)


def _put(storage: MemoryUserStorage, path: str, data: bytes) -> None:
    """Write test data into MemoryUserStorage."""
    with storage.fs.open(path, mode="wb") as f:
        f.write(data)


class TestSpecification:
    """Test suite for the Specification class"""

    @pytest.fixture
    def user_storage(self) -> MemoryUserStorage:
        """Create a MemoryUserStorage instance with test data"""
        storage = MemoryUserStorage()

        # Add schema xlsx file for table1
        schema_data = self._create_test_xlsx_schema()
        _put(storage, "specs/table1_schema.xlsx", schema_data)

        # Add rowcount SQL file for table1
        rowcount_sql = "SELECT COUNT(*) as __EXPECTED_ROWCOUNT__ FROM table1"
        _put(
            storage,
            "specs/table1_ROWCOUNT.sql",
            rowcount_sql.encode(),
        )

        # Add compare sample SQL file for table2
        compare_sql = "SELECT id, name FROM table2 WHERE id = 1 -- __EXPECTED__"
        _put(
            storage,
            "specs/table2_COMPARE.sql",
            compare_sql.encode(),
        )

        # Add schema file for table2 (for COMPARE which needs both)
        _put(storage, "specs/table2_schema.xlsx", schema_data)

        return storage

    @pytest.fixture
    def naming_conventions_factory(
        self,
    ) -> NamingConventionsFactory:
        """Create a NamingConventionsFactory instance"""
        return NamingConventionsFactory()

    @pytest.fixture
    def spec_parser_factory(self) -> SpecParserFactory:
        """Create a FormatterFactory instance"""
        return SpecParserFactory()

    @pytest.fixture
    def specification(
        self,
        user_storage: MemoryUserStorage,
        naming_conventions_factory: NamingConventionsFactory,
        spec_parser_factory: SpecParserFactory,
    ) -> Specification:
        """Create a Specification instance with all dependencies"""
        return Specification(
            user_storage=user_storage,
            naming_conventions_factory=naming_conventions_factory,
            parser_factory=spec_parser_factory,
        )

    def _create_test_xlsx_schema(self) -> bytes:
        """Create a test Excel file with schema data"""
        data = {
            "column": ["id", "name", "created_at"],
            "type": [
                "INTEGER",
                "VARCHAR(255)",
                "TIMESTAMP",
            ],
            "pk": ["x", "", ""],
            "partition": ["", "", "x"],
            "cluster": ["", "x", ""],
        }
        df = pl.DataFrame(data)

        buffer = io.BytesIO()
        df.write_excel(buffer, worksheet="schema")
        return buffer.getvalue()

    def test_init(self, specification: Specification):
        """Test that Specification initializes correctly"""
        assert specification.user_storage is not None
        assert specification.naming_conventions_factory is not None
        assert specification.parser_factory is not None

    def test_find_specs_schema(self, specification: Specification):
        """Test find_specs for schema test type"""
        location = LocationDTO("memory://specs/")
        testcase = TestCaseEntryDTO(
            testobject="table1", testtype=TestType.SCHEMA, domain="test_domain"
        )

        specs = specification.list_specs(location, testcase)

        assert len(specs) == 1
        assert isinstance(specs[0], SchemaSpecDTO)
        assert specs[0].testobject == "table1"
        assert specs[0].spec_type == SpecType.SCHEMA
        assert specs[0].columns is not None
        assert "id" in specs[0].columns
        assert "name" in specs[0].columns
        assert "created_at" in specs[0].columns

    def test_find_specs_rowcount(self, specification: Specification):
        """Test find_specs for rowcount test type"""
        location = LocationDTO("memory://specs/")
        testcase = TestCaseEntryDTO(
            testobject="table1", testtype=TestType.ROWCOUNT, domain="test_domain"
        )

        specs = specification.list_specs(location, testcase)

        assert len(specs) == 1
        assert isinstance(specs[0], RowcountSpecDTO)
        assert specs[0].testobject == "table1"
        assert specs[0].spec_type == SpecType.ROWCOUNT
        assert specs[0].query is not None
        assert "__EXPECTED_ROWCOUNT__" in specs[0].query

    def test_find_specs_compare(self, specification: Specification):
        """Test find_specs for compare sample test type"""
        location = LocationDTO("memory://specs/")
        testcase = TestCaseEntryDTO(
            testobject="table2", testtype=TestType.COMPARE, domain="test_domain"
        )

        specs = specification.list_specs(location, testcase)

        assert len(specs) == 2
        assert specs[0].spec_type == SpecType.COMPARE
        assert specs[1].spec_type == SpecType.SCHEMA

    def test_find_specs_no_matching_files(self, specification: Specification):
        """Test find_specs when no matching files are found"""
        location = LocationDTO("memory://specs/")
        testcase = TestCaseEntryDTO(
            testobject="nonexistent",
            testtype=TestType.SCHEMA,
            domain="test_domain",
        )

        specs = specification.list_specs(location, testcase)

        assert len(specs) == 0

    def test_find_specs_handles_parsing_errors(self, specification: Specification):
        """Test that find_specs gracefully handles parsing errors"""
        location = LocationDTO("memory://specs/")
        testcase = TestCaseEntryDTO(
            testobject="table1",
            testtype=TestType.SCHEMA,
            domain="test_domain",
        )

        error_spec = SchemaSpecDTO(
            location=location, testobject="table1", message="Parse error"
        )
        mock_parser = Mock()
        mock_parser.parse.return_value = error_spec

        with patch.object(
            specification.parser_factory,
            "get_parser",
            return_value=mock_parser,
        ):
            specs = specification.list_specs(location, testcase)
            assert len(specs) == 1
            assert specs[0].message == "Parse error"

    def test_find_specs_with_unsupported_test_type(self, specification: Specification):
        """Test find_specs with an unsupported test type"""
        location = LocationDTO("memory://specs/")
        testcase = TestCaseEntryDTO(
            testobject="table1",
            testtype=TestType.UNKNOWN,
            domain="test_domain",
        )

        with pytest.raises(SpecNamingConventionsError):
            specification.list_specs(location, testcase)

    def test_find_specs_handles_file_read_errors(self, specification: Specification):
        """Test that find_specs gracefully handles file read errors"""
        location = LocationDTO("memory://specs/")
        testcase = TestCaseEntryDTO(
            testobject="table1",
            testtype=TestType.SCHEMA,
            domain="test_domain",
        )

        mock_storage = Mock()
        mock_storage.list_objects.return_value = [
            LocationDTO("memory://specs/table1_schema.xlsx")
        ]
        mock_storage.read_object.side_effect = StorageError("Read error")

        with patch.object(
            specification,
            "user_storage",
            mock_storage,
        ):
            specs = specification.list_specs(location, testcase)
            assert len(specs) == 1
            assert specs[0].message == "Couldn't read file from storage"

    def test_find_specs_partial_success(
        self,
        specification: Specification,
        user_storage: MemoryUserStorage,
    ):
        """Test find_specs when some files parse successfully and others fail"""
        # Add a corrupted Excel file that will fail to parse
        _put(
            user_storage,
            "specs/table3_schema.xlsx",
            b"corrupted excel data",
        )

        # Also add a valid SQL file for same testobject
        sql_content = "SELECT COUNT(*) as __EXPECTED__ FROM table3"
        _put(
            user_storage,
            "specs/table3_COMPARE.sql",
            sql_content.encode(),
        )

        location = LocationDTO("memory://specs/")
        testcase = TestCaseEntryDTO(
            testobject="table3",
            testtype=TestType.COMPARE,
            domain="test_domain",
        )

        specs = specification.list_specs(location, testcase)

        assert len(specs) == 2
        successful = [s for s in specs if s.message is None]
        errors = [s for s in specs if s.message is not None]
        assert len(successful) == 1
        assert isinstance(successful[0], CompareSpecDTO)
        assert successful[0].testobject == "table3"
        assert successful[0].query is not None
        assert "__EXPECTED__" in successful[0].query
        assert len(errors) == 1
