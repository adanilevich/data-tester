from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
import polars as pl

from src.dtos.specifications import SchemaSpecificationDTO
from src.dtos.testcase import TestObjectDTO, DBInstanceDTO


class IBackend(ABC):
    # if the backend supports pushdown, compare_sample will delegate to backend
    supports_db_comparison: bool
    # if clustering/partitioning are supported, testcase schema compare them to specs
    supports_clustering: bool
    supports_partitions: bool
    # if backend enforces primary keys, testcase schema will compare them to specs
    supports_primary_keys: bool

    @abstractmethod
    def get_testobjects(self, db: DBInstanceDTO) -> List[str]:
        """Get a list of testobjects existing for given domain, stage and instance"""

    @abstractmethod
    def get_schema(self, testobject: TestObjectDTO) -> SchemaSpecificationDTO:
        """Get schema (column names and datatyples) of testobject."""

    @abstractmethod
    def get_schema_from_query(
            self, query: str, db: DBInstanceDTO) -> SchemaSpecificationDTO:
        """Get schema (column names and datatyples) of (translated) query."""

    @abstractmethod
    def harmonize_schema(self, schema: SchemaSpecificationDTO) -> SchemaSpecificationDTO:
        """Translate schema from DB-specific dtypes to conventions known by users"""

    @abstractmethod
    def translate_query(self, query: str, db: DBInstanceDTO) -> str:
        """
        Translates a user-provided test query to target database coordinates,
        e.g. technical parameters like stage, db schema are replaced such that the
        user doesnt have to change queries between stages.
        """

    @abstractmethod
    def run_query(self, query: str, db: DBInstanceDTO) -> pl.DataFrame:
        """
        Executes a query against the defined database. Client is responsible for
        translating the query using translate_query().
        """

    @abstractmethod
    def get_rowcount(
            self, testobject: TestObjectDTO,
            filters: Optional[List[Tuple[str, str]]] = None
    ) -> int:
        """
        Get rowcount of the specified testobject. If defined, additional filters
        are applied.
            - Filters are a list of 2-tuples (column_name, operation)
            - Hereby, column names must correspond to columns in testobject table or file
            - Operations to be supported are
                '=<value>': testobject will be filtered to only keep rows where the
                    specified column corresponds to this value
        """

    @abstractmethod
    def get_sample_keys(
            self, query: str, primary_keys: List[str], sample_size: int,
            db: DBInstanceDTO, cast_to: Optional[SchemaSpecificationDTO] = None
    ) -> List[str]:
        """
        Given a test sql (query), and a list of column names (which must be returned
        by the query), obtains a random sample of column values of defined size.
            - Client must translate the query via translate_query() first
            - Provided query must contain the expectation as '__expected__ AS ' CTE
        """

    @abstractmethod
    def get_sample_from_query(
            self, query: str, primary_keys: List[str], key_sample: List[str],
            db: DBInstanceDTO, columns: Optional[List[str]] = None,
            cast_to: Optional[SchemaSpecificationDTO] = None
    ) -> pl.DataFrame:
        """
        Given a test sql (query), a list of column names (interpreted as primary keys),
        a corresponding list of sample values, obtains a random sample
        of all columns from the query - e.g. samples data from a query based on
        provided examples of primary keys. If columns is provided, only these columns
        are selected.
            - Client must translate the query via translate_query() first
            - Provided query must contain the expectation as '__expected__ AS ' CTE
        """

    @abstractmethod
    def get_sample_from_testobject(
            self, testobject: TestObjectDTO, primary_keys: List[str],
            key_sample: List[str], columns: Optional[List[str]] = None,
            cast_to: Optional[SchemaSpecificationDTO] = None
    ) -> pl.DataFrame:
        """
        Given a list of column names (interpreted as primary keys) and a corresponding
        list of values, obtains a random sample of defined (or all) columns from the
        testobject.
        """
