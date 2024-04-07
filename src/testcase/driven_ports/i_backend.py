from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Union
from dataclasses import dataclass, asdict


@dataclass
class SchemaDTO:
    columns: Dict[str, str]  # schema as dict with keys 'column', 'dtype'
    primary_keys: Optional[List[str]] = None  # list of primary keys (if supported)
    partition_columns: Optional[List[str]] = None  # list of table partition keys
    clustering_columns: Optional[List[str]] = None  # lsit of table clustering keys

    def dict(self) -> Dict[str, Union[Dict, Optional[List]]]:
        return asdict(self)

    @classmethod
    def from_dict(cls, schema_as_dict: Dict):
        return cls(schema_as_dict)


class IBackend(ABC):

    # if the backend supports pushdown, compare_sample will delegate to backend
    supports_db_comparison: bool
    # if clustering/partitioning are supported, testcase schema compare them to specs
    supports_clustering: bool
    supports_partitions: bool
    # if backend enforces primary keys, testcase schema will compare them to specs
    supports_primary_keys: bool

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
