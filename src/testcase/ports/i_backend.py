from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple

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
    def get_testobjects(self, domain: str, stage: str, instance) -> List[str]:
        """Get a list of testobjects existing for given domain, stage and instance"""

    @abstractmethod
    def get_schema(self, domain: str, stage: str, instance: str,
                   testobject: str) -> SchemaSpecificationDTO:
        """Get schema (column names and datatyples) of testobject."""

    @abstractmethod
    def harmonize_schema(self, schema: SchemaSpecificationDTO) -> SchemaSpecificationDTO:
        """Translate schema from DB-specific dtypes to conventions known by users"""

    @abstractmethod
    def run_query(self, query: str, domain: str, stage: str, instance: str) \
            -> Dict[str, List[Any]]:
        """
        Executes a query against the database. Hereby, the query is translated to
        provided coordinates, e.g. stage, instance such that user doesn't have to
        rewrite his SQL statements when switching between testcases.
        """

    @abstractmethod
    def get_rowcount(self, domain: str, stage: str, instance: str, testobject: str,
                     filters: Optional[List[Tuple[str, str]]] = None) -> int:
        """
        Get rowcount of the specified testobject. If defined, additional filters
        are applied.
            - Filters are a list of 2-tuples (column_name, operation)
            - Hereby, column names must correspond to columns in testobject table or file
            - Operations to be supported are
                '=<value>': testobject will be filtered to only keep rows where the
                    specified column corresponds to this value
        """
