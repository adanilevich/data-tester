from abc import ABC, abstractmethod
from typing import List

from src.dtos.specifications import SchemaSpecificationDTO


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
                   testobject: str) -> SchemaSpecificationDTO:
        """Get schema (column names and datatyples) of testobject."""

    @abstractmethod
    def harmonize_schema(self, schema: SchemaSpecificationDTO) -> SchemaSpecificationDTO:
        """Translate schema from DB-specific dtypes to conventions known by users"""
