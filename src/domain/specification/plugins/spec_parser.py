import json
from typing import cast

import polars as pl

from src.dtos import (
    SpecType,
    SchemaSpecDTO,
    RowcountSpecDTO,
    CompareSpecDTO,
    StagecountSpecDTO,
)
from src.dtos.specification_dtos import SpecDTO
from .i_spec_parser import (
    ISpecParser,
    ISpecParserFactory,
    SpecParserError,
)


class XlsxSchemaParser(ISpecParser):
    """
    Implementation Parses schema information from an .xlsx file.
    """

    spec_type = SpecType.SCHEMA

    def parse(self, file: bytes, empty_spec: SpecDTO) -> SchemaSpecDTO:
        """
        Parse .xlsx file for database table schema definition.
        """
        try:
            df = pl.read_excel(file, sheet_name="schema")
        # broad exception catch since polars not always raises specific errors
        except Exception as e:
            spec = self.set_message(empty_spec, f"Error reading schema from .xlsx: {e}")
            spec = cast(SchemaSpecDTO, spec)
            return spec

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

        return SchemaSpecDTO(
            location=empty_spec.location,
            testobject=empty_spec.testobject,
            columns=columns,
            primary_keys=primary_keys,
            partition_columns=partition_columns,
            clustering_columns=clustering_columns,
        )


class RowcountSqlParser(ISpecParser):
    """
    Implementation Parses schema information from a .sql file.
    """

    spec_type = SpecType.ROWCOUNT

    def parse(self, file: bytes, empty_spec: SpecDTO) -> RowcountSpecDTO:
        try:
            content = file.decode("utf-8")
        except Exception as e:
            spec = self.set_message(empty_spec, f"Error decoding file: {e}")
            spec = cast(RowcountSpecDTO, spec)
            return spec

        if "__EXPECTED_ROWCOUNT__" in content:
            return RowcountSpecDTO(
                location=empty_spec.location,
                testobject=empty_spec.testobject,
                query=content,
            )
        else:
            spec = self.set_message(empty_spec, "Missing __EXPECTED_ROWCOUNT__")
            spec = cast(RowcountSpecDTO, spec)
            return spec


class CompareSqlParser(ISpecParser):
    """
    Implementation Parses compare information from a .sql file.
    """

    spec_type = SpecType.COMPARE

    def parse(self, file: bytes, empty_spec: SpecDTO) -> CompareSpecDTO:
        try:
            content = file.decode("utf-8")
        except Exception as e:
            spec = self.set_message(empty_spec, f"Error decoding file: {e}")
            return cast(CompareSpecDTO, spec)

        if "__EXPECTED__" in content:
            return CompareSpecDTO(
                location = empty_spec.location,
                testobject=empty_spec.testobject,
                query=content,
            )
        else:
            spec = self.set_message(empty_spec, "Missing __EXPECTED__")
            return cast(CompareSpecDTO, spec)


class StagecountJsonParser(ISpecParser):
    """Parses stagecount specification from a JSON file."""

    spec_type = SpecType.STAGECOUNT

    def parse(self, file: bytes, empty_spec: SpecDTO) -> StagecountSpecDTO:
        try:
            data = json.loads(file.decode("utf-8"))
        except Exception as e:
            spec = self.set_message(
                empty_spec, f"Error reading stagecount JSON: {e}",
            )
            return cast(StagecountSpecDTO, spec)

        return StagecountSpecDTO(
            location=empty_spec.location,
            testobject=empty_spec.testobject,
            raw_file_format=data.get("raw_file_format"),
            raw_file_encoding=data.get("raw_file_encoding"),
            skip_lines=data.get("skip_lines"),
        )


class SpecParserFactory(ISpecParserFactory):
    """
    Factory for picking right formatters. In real implementation, this factory should
    be extended to create the appropriate formatters for a given domain.
    """

    def get_parser(self, domain: str, spec_type: SpecType) -> ISpecParser:
        if spec_type == SpecType.SCHEMA:
            return XlsxSchemaParser()
        elif spec_type == SpecType.ROWCOUNT:
            return RowcountSqlParser()
        elif spec_type == SpecType.COMPARE:
            return CompareSqlParser()
        elif spec_type == SpecType.STAGECOUNT:
            return StagecountJsonParser()
        else:
            raise SpecParserError(f"Parsing {spec_type} is not supported")
