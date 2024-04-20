from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any, Optional, Dict, List, get_type_hints


@dataclass
class SpecificationDTO:
    location: str = "__no__default__"
    type: str = "__no_default__"

    @classmethod
    def from_dict(cls, spec_as_dict: dict) -> Any:  # 'Any' to not clash with subtypes
        # spec_as_dict may contain keys which are not required to construct a spec
        constructor_dict = {
            k: v for k, v in spec_as_dict.items() if k in get_type_hints(cls)
        }

        return cls(**constructor_dict)

    def __post_init__(self):
        if self.location == "__no__default__":
            raise ValueError("Spec location not defined")
        if self.type == "__no_default__":
            raise ValueError("Spec type not defined")

    def dict(self) -> dict:
        return asdict(self)


@dataclass
class SchemaSpecificationDTO(SpecificationDTO):
    type: str = "schema"
    # schema as dict with keys 'column', 'dtype'
    columns: Dict[str, str] = field(default_factory=dict)
    primary_keys: Optional[List[str]] = None  # list of primary keys (if supported)
    partition_columns: Optional[List[str]] = None  # list of table partition keys
    clustering_columns: Optional[List[str]] = None  # lsit of table clustering keys

    def __post_init__(self):
        super().__post_init__()
        if len(self.columns) == 0:
            raise ValueError("Schema specification must have non-empty columns.")

    @classmethod
    def from_dict(cls, *args, **kwargs) -> SchemaSpecificationDTO:
        return super().from_dict(*args, **kwargs)


@dataclass
class RowCountSqlDTO(SpecificationDTO):
    type: str = "rowcount_sql"
    query: str = ""

    def __post_init__(self):
        super().__post_init__()
        if self.query == "":
            raise ValueError("Please provide a non-empty rowcount query.")

    @classmethod
    def from_dict(cls, *args, **kwargs) -> RowCountSqlDTO:
        return super().from_dict(*args, **kwargs)


@dataclass
class CompareSampleSqlDTO(SpecificationDTO):
    type: str = "compare_sample_sql"
    query: str = ""

    def __post_init__(self):
        super().__post_init__()
        if self.query == "":
            raise ValueError("Please provide a non-empty compare sample query.")

    @classmethod
    def from_dict(cls, *args, **kwargs) -> CompareSampleSqlDTO:
        return super().from_dict(*args, **kwargs)
