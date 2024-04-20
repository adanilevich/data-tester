from __future__ import annotations

from typing import Dict, List, Optional, Self
from pydantic import model_validator, Field

from src.dtos.dto import DTO


class SpecificationDTO(DTO):
    location: str = Field(min_length=1)  # e.g. full path to .sql file or .xlsx spec file
    testobject: str = Field(min_length=1)  # name of the specified testobject
    type: str = Field(min_length=1)  # e.g. 'schema', 'rowcount_sql'
    url: str = Field(default="none", min_length=1)  # clickable path to URL
    display_name: str = ""  # name how specification is to be displayed to user
    content: Optional[str] = Field(default=None, min_length=1)  # base64 (file) content
    #  for downloading in frontend

    class Config:
        validate_assignment = True

    @model_validator(mode="after")
    def set_display_name(self) -> Self:
        if self.display_name == "":
            if self.location == "":
                self.display_name = self.testobject
            else:
                self.display_name = self.location
        return self


class SchemaSpecificationDTO(SpecificationDTO):
    type: str = "schema"
    columns: Dict[str, str]  # schema as dict with keys 'column', 'dtype'
    primary_keys: Optional[List[str]] = None  # list of primary keys (if supported)
    partition_columns: Optional[List[str]] = None  # list of table partition keys
    clustering_columns: Optional[List[str]] = None  # lsit of table clustering keys


class RowCountSqlDTO(SpecificationDTO):
    type: str = "rowcount_sql"
    query: str


class CompareSampleSqlDTO(SpecificationDTO):
    type: str = "compare_sample_sql"
    query: str


class SpecFactory:

    def create_from_dict(self, spec_as_dict: dict) -> SpecificationDTO:

        requested_spec_type = spec_as_dict["type"]
        known_spec_types = {
            cls_.model_fields["type"].default: cls_
            for cls_ in SpecificationDTO.__subclasses__()
        }
        if requested_spec_type in known_spec_types:
            spec_as_dict.pop("type")
            return known_spec_types[requested_spec_type].from_dict(spec_as_dict)
        else:
            raise ValueError(f"Unknown spec type: {requested_spec_type}")
