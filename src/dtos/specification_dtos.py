from __future__ import annotations
from enum import Enum
from typing import Callable, Dict, List, Optional, Self, Type
from pydantic import model_validator, Field

from src.dtos.dto import DTO
from src.dtos.storage_dtos import LocationDTO


class SpecType(Enum):
    """
    Specification Type is by purpose different from TestType: a testcase might require
    several specifications of different types, e.g. GENERAL and SCHEMA
    """

    SCHEMA = "schema"
    ROWCOUNT = "rowcount"
    COMPARE = "compare"
    STAGECOUNT = "stagecount"
    ABSTRACT = "abstract"


# registry of known spec types. Populated by SpecificationDTO.__init_subclass__
known_spec_types: Dict[str, Callable] = {}


class SpecDTO(DTO):
    location: LocationDTO
    testobject: str
    spec_type: SpecType = SpecType.ABSTRACT
    url: str | None = Field(default=None)  # clickable path to URL
    display_name: str | None = Field(default=None)
    message: str | None = Field(default=None)

    class Config:
        validate_assignment = True

    @property
    def empty(self) -> bool:
        return True

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


class SchemaSpecDTO(SpecDTO):
    spec_type: SpecType = SpecType.SCHEMA
    columns: Optional[Dict[str, str]] = None  # schema as dict with keys 'column', 'dtype'
    primary_keys: Optional[List[str]] = None  # list of primary keys (if supported)
    partition_columns: Optional[List[str]] = None  # list of table partition keys
    clustering_columns: Optional[List[str]] = None  # lsit of table clustering keys

    @property
    def empty(self) -> bool:
        return True if self.columns is None else False


class RowcountSpecDTO(SpecDTO):
    spec_type: SpecType = SpecType.ROWCOUNT
    query: Optional[str] = None

    @property
    def empty(self) -> bool:
        return True if self.query is None else False


class CompareSpecDTO(SpecDTO):
    spec_type: SpecType = SpecType.COMPARE
    query: Optional[str] = None

    @property
    def empty(self) -> bool:
        return True if self.query is None else False


class StagecountSpecDTO(SpecDTO):
    spec_type: SpecType = SpecType.STAGECOUNT
    raw_file_format: Optional[str] = None  # e.g. 'csv', 'json' — inferred if None
    raw_file_encoding: Optional[str] = None  # e.g. 'utf-8' — inferred if None
    skip_lines: Optional[int] = None  # header lines to skip — inferred if None

    @property
    def empty(self) -> bool:
        return False


# TODO: remove this and write from_dict classes
class SpecFactory:
    def create_from_dict(self, spec_as_dict: dict) -> SpecDTO:
        requested_spec_type = spec_as_dict["spec_type"]

        if requested_spec_type.lower() in known_spec_types:
            spec_as_dict_copy = spec_as_dict.copy()
            spec_as_dict_copy.pop("spec_type")
            spec_dto_class = known_spec_types[requested_spec_type.lower()]
            return spec_dto_class.from_dict(spec_as_dict_copy)  # type: ignore
        else:
            raise ValueError(f"Unknown spec type: {requested_spec_type}")


def spec_class_by_type(spec_type: SpecType) -> Type[SpecDTO]:
    if spec_type == SpecType.COMPARE:
        return CompareSpecDTO
    elif spec_type == SpecType.ROWCOUNT:
        return RowcountSpecDTO
    elif spec_type == SpecType.SCHEMA:
        return SchemaSpecDTO
    elif spec_type == SpecType.STAGECOUNT:
        return StagecountSpecDTO
    else:
        raise ValueError(f"Unknown spec type {spec_type}")
