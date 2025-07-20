import io
import pytest
import polars as pl

from src.dtos import (
    SpecificationType,
    SchemaContent,
    CompareSampleSqlContent,
    RowCountSqlContent,
)
from src.specification.adapters.formatter import (
    XlsxSchemaFormatter,
    SqlFormatter,
    FormatterFactory,
)


class TestXlsxSchemaFormatter:
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
        result = XlsxSchemaFormatter().deserialize(file_content)

        # Then the result is a SchemaContent object with the correct properties
        assert isinstance(result, SchemaContent)
        assert result.spec_type == SpecificationType.SCHEMA
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
        result = XlsxSchemaFormatter().deserialize(file_content)

        # Then the result is a SchemaContent object without partition and cluster columns
        assert isinstance(result, SchemaContent)
        assert result.spec_type == SpecificationType.SCHEMA
        assert result.columns == {
            "id": "INTEGER",
            "name": "VARCHAR(255)",
            "email": "VARCHAR(255)",
        }
        assert result.primary_keys == ["id"]
        assert result.partition_columns == []
        assert result.clustering_columns == []

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
        result = XlsxSchemaFormatter().deserialize(file_content)

        # Then the resulting SchemaContent does not contain the None column
        assert isinstance(result, SchemaContent)
        assert result.columns == {
            "id": "INTEGER",
            "name": "VARCHAR(255)",
            "email": "VARCHAR(255)",
        }
        assert result.primary_keys == ["id"]

class TestSqlFormatter:
    """Test cases for SqlFormatter class."""

    def test_deserialize_compare_sample_sql(self):
        # Given a compare sample sql file
        sql_content = """
        SELECT * FROM customers WHERE created_at > '2024-01-01';
        __EXPECTED__
        SELECT * FROM customers_expected WHERE created_at > '2024-01-01';
        """
        file_content = sql_content.encode("utf-8")

        # When
        result = SqlFormatter().deserialize(file_content)

        # Then
        assert isinstance(result, CompareSampleSqlContent)
        assert result.spec_type == SpecificationType.COMPARE_SAMPLE_SQL
        assert sql_content == result.query

    def test_deserialize_rowcount_sql(self):
        # Given a rowcount sql file
        sql_content = """
        SELECT COUNT(*) FROM transactions WHERE date = '2024-01-01';
        __EXPECTED_ROWCOUNT__
        1000
        """
        file_content = sql_content.encode("utf-8")

        # When
        result = SqlFormatter().deserialize(file_content)

        # Then
        assert isinstance(result, RowCountSqlContent)
        assert result.spec_type == SpecificationType.ROWCOUNT_SQL
        assert sql_content == result.query

    def test_deserialize_sql_without_markers_raises_error(self):
        # Given a sql file without __EXPECTED__ or __EXPECTED_ROWCOUNT__ markers
        sql_content = "SELECT * FROM customers;"
        file_content = sql_content.encode("utf-8")

        # When deserializing the file an error is raised
        with pytest.raises(ValueError, match="Unknown sql format"):
            SqlFormatter().deserialize(file_content)


class TestFormatterFactory:
    """Test cases for FormatterFactory class."""

    def test_get_formatter_for_schema(self):
        # Given a schema specification type
        factory = FormatterFactory()
        spec_type = SpecificationType.SCHEMA

        # When getting the formatter
        result = factory.get_formatter(spec_type)

        # Then the result is an XlsxSchemaFormatter instance
        assert isinstance(result, XlsxSchemaFormatter)

    def test_get_formatter_for_rowcount_sql(self):
        # Given a rowcount sql specification type
        factory = FormatterFactory()
        spec_type = SpecificationType.ROWCOUNT_SQL

        # When getting the formatter
        result = factory.get_formatter(spec_type)

        # Then the result is a SqlFormatter instance
        assert isinstance(result, SqlFormatter)

    def test_get_formatter_for_compare_sample_sql(self):
        # Given a compare sample sql specification type
        factory = FormatterFactory()
        spec_type = SpecificationType.COMPARE_SAMPLE_SQL

        # When getting the formatter
        result = factory.get_formatter(spec_type)

        # Then the result is a SqlFormatter instance
        assert isinstance(result, SqlFormatter)

    def test_get_formatter_for_unsupported_type_raises_error(self):
        # Given an unsupported specification type
        factory = FormatterFactory()
        class MockSpecType:
            pass
        unsupported_type = MockSpecType()

        # When getting the formatter an error is raised
        with pytest.raises(ValueError, match="Parsing.*is not supported"):
            factory.get_formatter(unsupported_type)  # type: ignore

    def test_formatter_factory_returns_different_instances(self):
        # Given multiple calls to get formatter
        factory = FormatterFactory()
        spec_type = SpecificationType.SCHEMA

        # When getting the formatter
        formatter1 = factory.get_formatter(spec_type)
        formatter2 = factory.get_formatter(spec_type)

        # Then the result is an XlsxSchemaFormatter instance
        assert isinstance(formatter1, XlsxSchemaFormatter)
        assert isinstance(formatter2, XlsxSchemaFormatter)
        assert formatter1 is not formatter2
