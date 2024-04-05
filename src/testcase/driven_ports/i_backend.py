from abc import ABC, abstractmethod
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class ColumnDTO:
    name: str
    dtype: str


@dataclass
class SchemaDTO:
    columns: List[ColumnDTO]

    def dict(self):
        return [{col.name: col.dtype} for col in self.columns]

    @classmethod
    def from_dict(cls, schema_as_dict: List[Dict[str, str]]):
        cols = []
        for col in schema_as_dict:
            cols.append(ColumnDTO(col["col"], col["dtype"]))
        return cls(cols)


class IBackend(ABC):

    supports_db_comparison: bool

    @abstractmethod
    def get_testobjects(self, domain: str, project: str, instance) -> List[str]:
        """Get a list of testobjects existing for given domain, project and instance"""

    @abstractmethod
    def get_schema(self, domain: str, project: str, instance: str,
                   testobject: str) -> SchemaDTO:
        """Get schema (column names and datatyples) of testobject."""

    @abstractmethod
    def harmonize_schema(self, schema: SchemaDTO) -> SchemaDTO:
        """Translate schema from DB-specific dtypes to conventions known by users"""
