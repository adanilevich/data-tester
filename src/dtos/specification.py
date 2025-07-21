from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional, Self
from pydantic import model_validator, Field

from src.dtos.dto import DTO
from src.dtos.location import LocationDTO


class SpecificationType(Enum):
    SCHEMA = "schema"
    ROWCOUNT_SQL = "rowcount_sql"
    COMPARE_SQL = "compare_sql"


class SpecificationFormat(Enum):
    SQL = "sql"
    XLSX = "xlsx"


class SpecificationDTO(DTO):
    location: LocationDTO
    testobject: str
    spec_type: SpecificationType
    url: str | None = Field(default=None)  # clickable path to URL
    display_name: str | None = Field(default=None)

    class Config:
        validate_assignment = True

    @model_validator(mode="after")
    def set_display_name(self) -> Self:
        if self.display_name == "":
            if self.location == "":
                self.display_name = self.testobject
            else:
                self.display_name = self.location.filename
        return self


class SpecContent(DTO):
    spec_type: SpecificationType


class SchemaContent(SpecContent):
    spec_type: SpecificationType = SpecificationType.SCHEMA
    columns: Dict[str, str]  # schema as dict with keys 'column', 'dtype'
    primary_keys: Optional[List[str]] = None  # list of primary keys (if supported)
    partition_columns: Optional[List[str]] = None  # list of table partition keys
    clustering_columns: Optional[List[str]] = None  # lsit of table clustering keys


class RowCountSqlContent(SpecContent):
    spec_type: SpecificationType = SpecificationType.ROWCOUNT_SQL
    query: str


class CompareSqlContent(SpecContent):
    spec_type: SpecificationType = SpecificationType.COMPARE_SQL
    query: str


class SchemaSpecificationDTO(SpecificationDTO):
    spec_type: SpecificationType = SpecificationType.SCHEMA
    columns: Dict[str, str]  # schema as dict with keys 'column', 'dtype'
    primary_keys: Optional[List[str]] = None  # list of primary keys (if supported)
    partition_columns: Optional[List[str]] = None  # list of table partition keys
    clustering_columns: Optional[List[str]] = None  # lsit of table clustering keys


class RowCountSqlDTO(SpecificationDTO):
    spec_type: SpecificationType = SpecificationType.ROWCOUNT_SQL
    query: str


class CompareSqlDTO(SpecificationDTO):
    spec_type: SpecificationType = SpecificationType.COMPARE_SQL
    query: str


class SpecFactory:
    def create_from_dict(self, spec_as_dict: dict) -> SpecificationDTO:
        requested_spec_type = spec_as_dict["spec_type"]
        known_spec_types = {
            cls_.model_fields["spec_type"].default.value: cls_
            for cls_ in SpecificationDTO.__subclasses__()
        }
        if (
            requested_spec_type in known_spec_types
            or requested_spec_type.lower() in known_spec_types
        ):
            spec_as_dict.pop("spec_type")
            return known_spec_types[requested_spec_type.lower()].from_dict(spec_as_dict)
        else:
            raise ValueError(f"Unknown spec type: {requested_spec_type}")
