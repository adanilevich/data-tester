from typing import List, Optional, Tuple

import polars as pl

from src.testcase.ports import IDataPlatform
from src.dtos import (
    SchemaSpecificationDTO, DBInstanceDTO, TestObjectDTO, SpecificationType
)


class DummyPlatform(IDataPlatform):
    """Dummy backend for test purpose only"""

    supports_db_comparison = False

    def get_testobjects(self, db: DBInstanceDTO) -> List[str]:
        return ["testobject1", "testobject2"]

    def get_schema(self, testobject: TestObjectDTO) -> SchemaSpecificationDTO:
        return SchemaSpecificationDTO(
            location="my_loc",
            testobject=testobject.name,
            columns={"my_col": "my_dtype"},
            spec_type=SpecificationType.SCHEMA,
            )

    def get_schema_from_query(
            self, query: str, db: DBInstanceDTO) -> SchemaSpecificationDTO:
        return SchemaSpecificationDTO(
            location="my_loc",
            testobject="user query",
            columns={"my_col": "my_dtype"},
            spec_type=SpecificationType.SCHEMA,
        )

    def harmonize_schema(self, schema: SchemaSpecificationDTO) -> SchemaSpecificationDTO:
        return schema

    def translate_query(self, query: str, db: DBInstanceDTO) -> str:
        return query

    def run_query(self, query: str, db: DBInstanceDTO) -> pl.DataFrame:
        return pl.DataFrame({"col": [1, 2, 3]})

    def get_rowcount(self, testobject: TestObjectDTO,
                     filters: Optional[List[Tuple[str, str]]] = None) -> int:
        return 10

    def get_sample_keys(
            self, query: str, primary_keys: List[str], sample_size: int,
            db: DBInstanceDTO, cast_to: Optional[SchemaSpecificationDTO] = None
    ) -> List[str]:
        return ["a_10", "b_20"]

    def get_sample_from_query(
            self, query: str, primary_keys: List[str], key_sample: List[str],
            db: DBInstanceDTO, columns: Optional[List[str]] = None,
            cast_to: Optional[SchemaSpecificationDTO] = None
    ) -> pl.DataFrame:
        return pl.DataFrame({"a": [10, 20], "b": [30, 40]})

    def get_sample_from_testobject(
            self, testobject: TestObjectDTO, primary_keys: List[str],
            key_sample: List[str], columns: Optional[List[str]] = None,
            cast_to: Optional[SchemaSpecificationDTO] = None
    ) -> pl.DataFrame:
        return pl.DataFrame({"a": [10, 20], "b": [30, 40]})
