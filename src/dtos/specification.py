from __future__ import annotations
from enum import Enum
from typing import Callable, Dict, List, Optional, Self
from pydantic import model_validator, Field

from src.dtos.dto import DTO
from src.dtos.storage import LocationDTO


class SpecificationType(Enum):
    SCHEMA = "schema"
    ROWCOUNT_SQL = "rowcount_sql"
    COMPARE_SQL = "compare_sql"


class SpecificationFormat(Enum):
    SQL = "sql"
    XLSX = "xlsx"

# registry of known spec types. Populated by SpecificationDTO.__init_subclass__
known_spec_types: Dict[str, Callable] = {}


class SpecificationDTO(DTO):
    location: LocationDTO
    testobject: str
    spec_type: SpecificationType
    url: str | None = Field(default=None)  # clickable path to URL
    display_name: str | None = Field(default=None)

    class Config:
        validate_assignment = True

    def __init_subclass__(cls, **kwargs) -> None:
        """Registers all implemented subclasses of AbstractCheck in known_checks"""
        super().__init_subclass__(**kwargs)
        spec_type = cls.spec_type.value.lower()
        known_spec_types[spec_type] = cls

    @model_validator(mode="after")
    def set_display_name(self) -> Self:
        if self.display_name == "" or self.display_name is None:
            if self.location.path == "":
                self.display_name: str = self.testobject
            else:
                self.display_name: str = self.location.filename or self.testobject
        return self


class SpecContent(DTO):
    spec_type: SpecificationType


# TODO: What do we use SchemaContent for if we SpecificationDTO?
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

        if requested_spec_type.lower() in known_spec_types:
            spec_as_dict_copy = spec_as_dict.copy()
            spec_as_dict_copy.pop("spec_type")
            spec_dto_class = known_spec_types[requested_spec_type.lower()]
            return spec_dto_class.from_dict(spec_as_dict_copy)  # type: ignore
        else:
            raise ValueError(f"Unknown spec type: {requested_spec_type}")
