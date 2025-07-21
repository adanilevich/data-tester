import polars as pl

from src.dtos import (
    SpecContent,
    SchemaContent,
    SpecificationType,
    CompareSqlContent,
    RowCountSqlContent,
)
from src.specification.ports import ISpecFormatter, ISpecFormatterFactory


class XlsxSchemaFormatter(ISpecFormatter):
    """
    Implementation Parses schema information from an .xlsx file.
    """

    def deserialize(self, file: bytes) -> SpecContent:
        """
        Parse .xlsx file for database table schema definition.
        """
        df = pl.read_excel(file, sheet_name="schema")
        records = df.to_dicts()

        # extract columns
        columns = {r["column"]: r["type"] for r in records if r["column"] is not None}

        # extract primary keys
        primary_keys = [
            r["column"]
            for r in records
            if r["pk"] in ["x", "X"] and r["column"] is not None
        ]

        # extract partition columns
        if "partition" in df.columns:
            partition_columns = [
                r["column"]
                for r in records
                if r["partition"] in ["x", "X"] and r["column"] is not None
            ]
        else:
            partition_columns = []

        # extract clustering columns
        if "cluster" in df.columns:
            clustering_columns = [
                r["column"]
                for r in records
                if r["cluster"] in ["x", "X"] and r["column"] is not None
            ]
        else:
            clustering_columns = []

        return SchemaContent(
            columns=columns,
            primary_keys=primary_keys,
            partition_columns=partition_columns,
            clustering_columns=clustering_columns,
        )


class RowcountSqlFormatter(ISpecFormatter):
    """
    Implementation Parses schema information from a .sql file.
    """

    def deserialize(self, file: bytes) -> SpecContent:
        content = file.decode("utf-8")
        result: SpecContent

        if "__EXPECTED_ROWCOUNT__" in content:
            spec_type = SpecificationType.ROWCOUNT_SQL
            result = RowCountSqlContent(
                query=content,
                spec_type=spec_type,
            )
        else:
            msg = "Unknown sql format. Missing __EXPECTED_ROWCOUNT__"
            raise ValueError(msg)

        return result


class CompareSqlFormatter(ISpecFormatter):
    """
    Implementation Parses compare information from a .sql file.
    """

    def deserialize(self, file: bytes) -> SpecContent:
        content = file.decode("utf-8")
        result: SpecContent

        if "__EXPECTED__" in content:
            spec_type = SpecificationType.COMPARE_SQL
            result = CompareSqlContent(
                query=content,
                spec_type=spec_type,
            )
        else:
            msg = "Unknown sql format. Missing __EXPECTED__"
            raise ValueError(msg)

        return result


class FormatterFactory(ISpecFormatterFactory):
    """
    Factory for picking right formatters. In real implementation, this factory should
    be extended to create the appropriate formatters for a given domain.
    """

    def get_formatter(self, spec_type: SpecificationType) -> ISpecFormatter:
        if spec_type == SpecificationType.SCHEMA:
            return XlsxSchemaFormatter()
        elif spec_type == SpecificationType.ROWCOUNT_SQL:
            return RowcountSqlFormatter()
        elif spec_type == SpecificationType.COMPARE_SQL:
            return CompareSqlFormatter()
        else:
            msg = f"Parsing {spec_type} is not supported"
            raise ValueError(msg)
