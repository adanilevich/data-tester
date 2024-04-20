from __future__ import annotations

from typing import Any, Dict, List, Optional
from src.dtos import DTO


class SpecificationDTO(DTO):
    location: str
    type: str

    # for type annotations
    @classmethod
    def from_dict(cls, spec_as_dict: dict) -> Any:
        return cls(**spec_as_dict)


class SchemaSpecificationDTO(SpecificationDTO):
    type: str = "schema"
    columns: Dict[str, str]  # schema as dict with keys 'column', 'dtype'
    primary_keys: Optional[List[str]] = None  # list of primary keys (if supported)
    partition_columns: Optional[List[str]] = None  # list of table partition keys
    clustering_columns: Optional[List[str]] = None  # lsit of table clustering keys

    # for type annotations
    @classmethod
    def from_dict(cls, *args, **kwargs) -> SchemaSpecificationDTO:
        return super().from_dict(*args, **kwargs)


class RowCountSqlDTO(SpecificationDTO):
    type: str = "rowcount_sql"
    query: str

    # for type annotations
    @classmethod
    def from_dict(cls, *args, **kwargs) -> RowCountSqlDTO:
        return super().from_dict(*args, **kwargs)


class CompareSampleSqlDTO(SpecificationDTO):
    type: str = "compare_sample_sql"
    query: str

    # for type annotations
    @classmethod
    def from_dict(cls, *args, **kwargs) -> CompareSampleSqlDTO:
        return super().from_dict(*args, **kwargs)
