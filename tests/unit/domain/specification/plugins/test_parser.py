from src.domain.specification.plugins.i_spec_parser import SpecParserError
import io
import pytest
import polars as pl

from src.dtos import (
    SpecType,
    CompareSpecDTO,
    SchemaSpecDTO,
    RowcountSpecDTO,
    SpecDTO,
    LocationDTO,
)
from src.domain.specification.plugins import (
    XlsxSchemaParser,
    RowcountSqlParser,
    CompareSqlParser,
    SpecParserFactory,
)


def _make_spec(spec_type: SpecType) -> SpecDTO:
    testobject = "to"
    loc = LocationDTO("memory://any")
    if spec_type == SpecType.COMPARE:
        return CompareSpecDTO(location=loc, testobject=testobject)
    elif spec_type == SpecType.ROWCOUNT:
        return RowcountSpecDTO(location=loc, testobject=testobject)
    elif spec_type == SpecType.SCHEMA:
        return SchemaSpecDTO(location=loc, testobject=testobject)
    else:
        raise ValueError("Error in tests: unknown spec type")


class TestXlsxSchemaParser:
    """Test cases for XlsxSchemaFormatter class."""

    def test_deserialize_basic_schema(self):
        # Given a correct excel based schema specification
        data = {
            "column": ["id", "name", "email", "created_at"],
            "type": ["INTEGER", "VARCHAR(255)", "VARCHAR(255)", "TIMESTAMP"],
            "pk": [None, "X", "x", None],
            "partition": [None, None, None, "x"],
            "cluster": [None, None, "x", None],
        }
        df = pl.DataFrame(data)
        excel_buffer = io.BytesIO()
        df.write_excel(excel_buffer, worksheet="schema")
        excel_buffer.seek(0)
        file_content = excel_buffer.read()

        # When deserializing the file
        empty_spec = _make_spec(spec_type=SpecType.SCHEMA)
        result = XlsxSchemaParser().parse(file_content, empty_spec)

        # Then the result is a SchemaContent object with the correct properties
        assert isinstance(result, SchemaSpecDTO)
        assert result.columns == {
            "id": "INTEGER",
            "name": "VARCHAR(255)",
            "email": "VARCHAR(255)",
            "created_at": "TIMESTAMP",
        }
        assert result.primary_keys == ["name", "email"]
        assert result.partition_columns == ["created_at"]
        assert result.clustering_columns == ["email"]

    def test_deserialize_schema_without_partition_cluster_columns(self):
        # Given a schema xlsx file without partition and cluster columns
        data = {
            "column": ["id", "name", "email"],
            "type": ["INTEGER", "VARCHAR(255)", "VARCHAR(255)"],
            "pk": ["x", None, None],
        }
        df = pl.DataFrame(data)
        excel_buffer = io.BytesIO()
        df.write_excel(excel_buffer, worksheet="schema")
        excel_buffer.seek(0)
        file_content = excel_buffer.read()

        # When deserializing the file
        empty_spec = _make_spec(spec_type=SpecType.SCHEMA)
        result = XlsxSchemaParser().parse(file_content, empty_spec)

        # Then the result is a SchemaContent object without partition and cluster columns
        assert isinstance(result, SchemaSpecDTO)
        assert result.spec_type == SpecType.SCHEMA
        assert result.columns == {
            "id": "INTEGER",
            "name": "VARCHAR(255)",
            "email": "VARCHAR(255)",
        }
        assert result.primary_keys == ["id"]
        assert result.partition_columns == []
        assert result.clustering_columns == []
        assert not result.empty

    def test_deserialize_schema_with_none_columns(self):
        # Given a schema xlsx file with None columns
        data = {
            "column": ["id", "name", None, "email"],
            "type": ["INTEGER", "VARCHAR(255)", "VARCHAR(255)", "VARCHAR(255)"],
            "pk": ["x", None, None, None],
        }
        df = pl.DataFrame(data)
        excel_buffer = io.BytesIO()
        df.write_excel(excel_buffer, worksheet="schema")
        excel_buffer.seek(0)
        file_content = excel_buffer.read()

        # When deserializing the file
        empty_spec = _make_spec(spec_type=SpecType.SCHEMA)
        result = XlsxSchemaParser().parse(file_content, empty_spec)

        # Then the resulting SchemaContent does not contain the None column
        assert isinstance(result, SchemaSpecDTO)
        assert result.columns == {
            "id": "INTEGER",
            "name": "VARCHAR(255)",
            "email": "VARCHAR(255)",
        }
        assert result.primary_keys == ["id"]
        assert not result.empty


class TestSqlParser:
    """Test cases for SqlFormatter class."""

    def test_deserialize_compare_sql(self):
        # Given a compare sql file
        sql_content = """
        SELECT * FROM customers WHERE created_at > '2024-01-01';
        __EXPECTED__
        SELECT * FROM customers_expected WHERE created_at > '2024-01-01';
        """
        file_content = sql_content.encode("utf-8")

        # When
        empty_spec = _make_spec(spec_type=SpecType.COMPARE)
        result = CompareSqlParser().parse(file_content, empty_spec)

        # Then
        assert isinstance(result, CompareSpecDTO)
        assert sql_content == result.query
        assert not result.empty

    def test_deserialize_rowcount_sql(self):
        # Given a rowcount sql file
        sql_content = """
        SELECT COUNT(*) FROM transactions WHERE date = '2024-01-01';
        __EXPECTED_ROWCOUNT__
        1000
        """
        file_content = sql_content.encode("utf-8")

        # When
        empty_spec = _make_spec(spec_type=SpecType.ROWCOUNT)
        result = RowcountSqlParser().parse(file_content, empty_spec)

        # Then
        assert isinstance(result, RowcountSpecDTO)
        assert sql_content == result.query
        assert not result.empty

    def test_deserialize_sql_without_markers_raises_error(self):
        # Given a sql file without __EXPECTED__ or __EXPECTED_ROWCOUNT__ markers
        sql_content = "SELECT * FROM customers;"
        file_content = sql_content.encode("utf-8")

        empty_spec = _make_spec(spec_type=SpecType.ROWCOUNT)
        result = RowcountSqlParser().parse(file_content, empty_spec)

        # Spec should be empty
        assert result.empty


class TestParserFactory:
    """Test cases for FormatterFactory class."""

    def test_get_parser_for_schema(self):
        factory = SpecParserFactory()
        result = factory.get_parser("test_domain", SpecType.SCHEMA)
        assert isinstance(result, XlsxSchemaParser)

    def test_get_parser_for_rowcount(self):
        factory = SpecParserFactory()
        result = factory.get_parser("test_domain", SpecType.ROWCOUNT)
        assert isinstance(result, RowcountSqlParser)

    def test_get_parser_for_compare(self):
        factory = SpecParserFactory()
        result = factory.get_parser("test_domain", SpecType.COMPARE)
        assert isinstance(result, CompareSqlParser)

    def test_get_parser_for_unsupported_type_raises_error(self):
        factory = SpecParserFactory()
        with pytest.raises(SpecParserError, match="Parsing.*is not supported"):
            factory.get_parser("test_domain", SpecType.ABSTRACT)
