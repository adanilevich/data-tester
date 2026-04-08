from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Callable, Dict, List, Optional, Self, Union

from pydantic import Discriminator, Field, Tag, model_validator

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

    @classmethod
    def from_dict(cls, dict_: dict) -> "AnySpec":
        spec_type = dict_.get("spec_type")
        if spec_type is None:
            raise ValueError(f"Spec type missing in dict: {dict_}")
        if isinstance(spec_type, SpecType):
            spec_type_val = spec_type.value.lower()
        elif isinstance(spec_type, str):
            spec_type_val = spec_type.lower()
        else:
            raise ValueError(f"spec_type of unknown type: {spec_type}")
        concrete_cls = known_spec_types.get(spec_type_val)
        if concrete_cls is None:
            raise ValueError(f"Unkown spec type: {spec_type}")
        # Strip spec_type from the dict: each concrete class declares it as a
        # Literal[SpecType.X] field with a default, so passing the serialized
        # string value would fail Pydantic's strict Literal validation.
        return concrete_cls(**{k: v for k, v in dict_.items() if k != "spec_type"})

    @classmethod
    def from_type(cls, spec_type: SpecType, **kwargs) -> "AnySpec":
        cls = known_spec_types.get(spec_type.value.lower())
        if cls is None:
            raise ValueError(f"Unkown spec type: {spec_type}")
        return cls(spec_type=spec_type, **kwargs)


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


def _spec_discriminator(v: Any) -> str | None:
    """Extract the spec_type string for routing the discriminated union.

    Accepts both already-instantiated SpecDTO subclasses (Python objects) and
    raw dicts from JSON deserialization.  Returns the lower-case ``spec_type``
    string that ``Tag(...)`` annotations on each union member are keyed on.
    """
    if isinstance(v, SpecDTO):
        return v.spec_type.value
    if isinstance(v, dict):
        spec_type = v.get("spec_type")
        if isinstance(spec_type, SpecType):
            return spec_type.value
        if isinstance(spec_type, str):
            return spec_type.lower()
    return None


AnySpec = Annotated[
    Union[
        Annotated[SchemaSpecDTO, Tag(SpecType.SCHEMA.value)],
        Annotated[RowcountSpecDTO, Tag(SpecType.ROWCOUNT.value)],
        Annotated[CompareSpecDTO, Tag(SpecType.COMPARE.value)],
        Annotated[StagecountSpecDTO, Tag(SpecType.STAGECOUNT.value)],
    ],
    Discriminator(_spec_discriminator),
]
"""Pydantic v2 discriminated union for polymorphic SpecDTO deserialization.

WHY THIS EXISTS
---------------
Pydantic v2 behaves differently depending on whether it validates data from a
Python object (``model_validate``) or from JSON bytes (``model_validate_json`` /
FastAPI request body).

When a field is annotated as ``List[SpecDTO]`` and the incoming data is JSON,
Pydantic's JSON-mode validator rebuilds every element using *only* the base
``SpecDTO`` schema.  Even if a ``mode="before"`` validator has already converted
the raw dict into a ``SchemaSpecDTO`` instance, Pydantic's JSON path discards
subclass-specific fields (``columns``, ``query``, etc.) and produces an object
whose type label is correct (``SchemaSpecDTO``) but whose data is gone —
``columns`` is ``None``, ``empty`` returns ``True``, and every testcase that
depends on that spec ends with N/A.

This was confirmed with:

    ta = TypeAdapter(List[List[SpecDTO]])
    ta.validate_python([[schema_spec]])  # → SchemaSpecDTO, columns={'id': 'INT'}  ✓
    ta.validate_json(json_data)          # → SchemaSpecDTO, columns=None            ✗

WHY A FUNCTION DISCRIMINATOR (NOT ``Field(discriminator="spec_type")``)
-----------------------------------------------------------------------
Pydantic v2's standard ``Field(discriminator=...)`` requires each union member
to declare its discriminator field with a ``Literal[EnumValue]`` type annotation
(e.g. ``spec_type: Literal[SpecType.SCHEMA]``).  However, ``Literal`` types in
Pydantic are strict — they reject string-to-enum coercion and require the exact
enum member object.  This breaks:

* Deserialization from storage (JSON-parsed dicts contain ``spec_type: "schema"``,
  a plain string, not ``SpecType.SCHEMA``).
* Direct construction from ``to_dict()`` output, which serializes enums as
  strings by default.
* Any code path that passes a string spec_type to the constructor.

The function-based ``Discriminator`` sidesteps this entirely.  The
``_spec_discriminator`` function accepts both ``SpecType`` enum values and plain
strings, extracts the lower-case string tag, and routes to the right model.
Each subclass continues to declare ``spec_type: SpecType`` (not ``Literal``),
so enum-to-string coercion still works in all Pydantic validation modes.

HOW THE FIX WORKS
-----------------
``_spec_discriminator`` is called first, before any model validation.  It reads
``spec_type`` from the incoming dict or object and returns a string tag (e.g.
``"schema"``).  Pydantic then dispatches to the ``Tag``-annotated union member
whose tag matches.  Because Pydantic now knows the exact target model, it uses
the full subclass schema in both Python and JSON modes — no data is lost.

USAGE
-----
Use ``AnySpec`` (not ``SpecDTO``) wherever Pydantic needs to *deserialize* specs
from JSON or plain dicts — typically in request bodies and persisted DTOs:

    class ExecuteTestRunRequest(DTO):
        specs: List[List[AnySpec]]

    class TestDefinitionDTO(DTO):
        specs: List[AnySpec]

Everywhere specs are already concrete Python instances (inside testcase logic,
precondition checks, etc.) ``SpecDTO`` remains the correct base-class annotation
and no change is needed there.
"""
