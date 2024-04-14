from __future__ import annotations

from dataclasses import replace
from typing import List, Tuple, Optional
from random import randint

import duckdb
import polars as pl
from fsspec.implementations.local import LocalFileSystem  # type: ignore

from src.testcase.adapters.backends.local import (
    DemoNamingResolver, DemoQueryHandler
)
from src.testcase.ports.i_backend import IBackend
from src.dtos.specifications import SchemaSpecificationDTO
from src.dtos.configs import DomainConfigDTO
from src.dtos.testcase import TestObjectDTO, DBInstanceDTO


class LocalBackend(IBackend):
    """
    Local backend: File storage is simply data stored on disks. Table storage is a
    duckdb-based DWH. This backend is implemented mainly for demo purpose and purpose
    of integration tests.

    For resolving business naming conventions to technical paths (e.g. db names),
    a NamingResolver needs to be provided, which is used by almost all methods
    which operate on 'domain', 'stage' or 'instance' keywords in their signature.

    For translating test queries provided by business to different instances and stages
    of database, a QueryHandler must be provided.
    """

    supports_db_comparison = False
    supports_clustering = False
    supports_partitions = False
    supports_primary_keys = False

    def __init__(self, files_path: str, db_path: str, domain_config: DomainConfigDTO,
                 naming_resolver: DemoNamingResolver, query_handler: DemoQueryHandler,
                 fs: Optional[LocalFileSystem] = None, db=duckdb):
        """
        Initialize backend.

        Args:
            files_path: path in local file system where file-like objects are stored,
                e.g. raw or export layers of local DWH
            db_path: path in local file system where all duckdb .db files are located
                on top-level
            domain_config: domain config which is used to configure handlers
            naming_resolver: resolver object which translates between business naming
                conventions for testobjects and technical coordinates
            query_handler: translates user-provided SQL queries to required stage/instance
        """

        self.files_path: str = files_path
        self.db_path: str = db_path
        self.config: DomainConfigDTO = domain_config
        self.naming_resolver: DemoNamingResolver = naming_resolver
        self.query_handler: DemoQueryHandler = query_handler
        self.fs: LocalFileSystem = fs or LocalFileSystem()
        self.duckdb = db

        # initialize databases
        self._init_dbs()

    def _init_dbs(self):
        """Initialize duckdb databases from .db files in specified location"""
        db_files = [f for f in self.fs.ls(self.db_path) if f.endswith(".db")]
        for db_file in db_files:
            db_name = db_file.split("/")[-1].removesuffix(".db")
            self.duckdb.execute(f"ATTACH IF NOT EXISTS '{db_file}' AS {db_name}")

    def get_testobjects(self, db: DBInstanceDTO) -> List[str]:
        """
        Gets both file-like testobjects (e.g. file directories in raw layer)
        and existing testobjects from db, e.g. tables and views.
        """

        # FIRST: get file-like testobjects
        # For that, get base paths to file like objects - these could be several paths,
        # e.g. <base_path>/raw and <base_path>/export
        rel_filepaths: List[str] = self.naming_resolver.resolve_files(db=db)
        abs_filepaths = [self.files_path + "/" + path_ for path_ in rel_filepaths]

        file_testobjects: List[str] = []
        for filepath in abs_filepaths:
            for file_or_dir in self.fs.ls(filepath):
                if self.fs.isdir(file_or_dir):
                    # TODO: this is actually bad - naming conventions leak into Backend!
                    # implement a resolver function 'get_object_name' instead
                    testobject_name = "raw_" + file_or_dir.split("/")[-1]
                    file_testobjects.append(testobject_name)

        # SECOND, get testobjects from dwh / database layer
        catalog, schema, _ = self.naming_resolver.resolve_db(db=db)
        query = f"""
            SELECT table_name FROM INFORMATION_SCHEMA.TABLES
            WHERE table_catalog = '{catalog}'
            AND table_schema = '{schema}'
        """
        tables_df = self.duckdb.query(query).pl()

        db_testobject = tables_df.to_dict(as_series=False)["table_name"]

        return file_testobjects + db_testobject

    def get_rowcount(
            self, testobject: TestObjectDTO,
            filters: Optional[List[Tuple[str, str]]] = None
    ) -> int:
        """See interface definition (parent class IBackend)."""

        object_type = self.naming_resolver.get_object_type(testobject=testobject)
        if object_type == object_type.FILE:
            count = self._get_file_rowcount(testobject, filters)
        else:
            count = self._get_db_rowcount(testobject, filters)

        return count

    def _get_db_rowcount(
            self, testobject: TestObjectDTO,
            filters: Optional[List[Tuple[str, str]]] = None,
    ) -> int:

        filters_: List[Tuple[str, str]] = filters or []
        db = DBInstanceDTO(testobject.domain, testobject.stage, testobject.instance)
        catalog, schema, table = self.naming_resolver.resolve_db(db, testobject.name)

        where_clause = "WHERE 1 = 1"
        for column_name, operation in filters_:
            if operation.startswith("="):
                value = operation.removeprefix("=")
                where_clause += (
                    f"\n\tAND {column_name} == {value}"
                    f" FROM {catalog}.{schema}.{table}"
                )

        query = f"""
            SELECT COUNT(*) AS __cnt__ FROM {catalog}.{schema}.{table}
            {where_clause}
        """
        count_df = self.duckdb.query(query).pl()

        count_dict = count_df.to_dict(as_series=False)  # dict {colname: [values]}
        count = count_dict["__cnt__"][0]

        return count

    def _get_file_rowcount(
            self, testobject: TestObjectDTO,
            filters: Optional[List[Tuple[str, str]]] = None
    ) -> int:
        raise ValueError("Getting rowcount for file-like testobjects (e.g. raw "
                         "layer) is not yet supported.")

    def translate_query(self, query: str, db: DBInstanceDTO) -> str:
        translated_query = self.query_handler.translate(query, db)
        return translated_query

    def run_query(self, query: str) -> pl.DataFrame:
        """See interface definition (parent class IBackend)."""

        result_as_df = self.duckdb.query(query).pl()

        return result_as_df

    def get_schema(self, testobject: TestObjectDTO) -> SchemaSpecificationDTO:
        """
        Gets table schema from duckdb, harmonizes datatypes according to conventions and
        returns results. Schema retrieval of file objects is not supported.
        """

        object_type = self.naming_resolver.get_object_type(testobject)
        if object_type == object_type.FILE:
            raise ValueError("Getting schema for file-like testobjects (e.g. raw "
                             "layer) is not supported.")

        db = DBInstanceDTO(testobject.domain, testobject.stage, testobject.instance)
        catalog, schema, table = self.naming_resolver.resolve_db(db, testobject.name)

        schema_query = f"""
                SELECT column_name AS col, data_type AS dtype
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE table_catalog = '{catalog}'
                AND table_schema = '{schema}'
                AND table_name = '{table}'
            """

        # convert to polars dataframe with columns 'col', 'dtype'
        schema_as_df = self.duckdb.query(schema_query).pl()
        # convert to dict with keys 'col', 'dtype' and value-lists as values
        schema_as_named_dict = schema_as_df.to_dict(as_series=False)
        # convert to a dict with column names as keys and dtypes as values
        schema_as_dict = dict(
            zip(schema_as_named_dict["col"], schema_as_named_dict["dtype"])
        )

        result = SchemaSpecificationDTO(
            location=".".join(testobject.dict().values()),
            columns=schema_as_dict,
        )

        return result

    def harmonize_schema(self, schema: SchemaSpecificationDTO) -> SchemaSpecificationDTO:
        """
        In our DWH stage, the convention is that datatypes are relevant for comparison
        only in their simplified form, e.g. complex datatypes like ARRAY, STRUCT are
        not relevant for automated comparisons. Here, a harmonization between
        duckdb dtypes and aligned conventions take place.

        Args:
            schema: original duckdb schema as list of dicts with keys 'col', 'dtype

        Return:
            schema: corresponding (simplified and unified) schema which is
                understood and refered to by data experts from business, e.g.
                    -'DECIMAL', 'NUMERIC', are translated to 'decimal'
                    - 'TEXT', 'STRING', 'VARCHAR(n)' are translated to 'string'
        """

        harmonized_columns = {}
        for column_name, dtype in schema.columns.items():
            dtype = dtype.lower()
            complex_dtypes = ["array", "list", "interval", "struct"]

            # if dtype contains one of the complex dtype keywords, we return it as is
            # reason is that comparisons with complex dtypes are not supported
            if any([complex_dtype in dtype for complex_dtype in complex_dtypes]):
                harmonized_dtype = dtype
            elif "int" in dtype:
                harmonized_dtype = "int"
            elif "date" in dtype:
                harmonized_dtype = "date"
            elif "timestamp" in dtype:
                harmonized_dtype = "timestamp"
            elif "string" in dtype or "text" in dtype or "char" in dtype:
                harmonized_dtype = "string"
            elif "numeric" in dtype or "decimal" in dtype:
                harmonized_dtype = "decimal"
            elif "float" in dtype or "real" in dtype or "double" in dtype:
                harmonized_dtype = "float"
            else:
                harmonized_dtype = dtype

            harmonized_columns.update({column_name: harmonized_dtype})

        harmonized_schema_dto = replace(schema)
        harmonized_schema_dto.columns = harmonized_columns

        return harmonized_schema_dto

    @staticmethod
    def _get_concat_key(primary_keys: List[str]) -> str:
        concat_key = ", '|', ".join([f"CAST({key} AS STRING)" for key in primary_keys])
        return f"CONCAT({concat_key})"

    @staticmethod
    def _get_column_selection(columns: Optional[List[str]] = None) -> str:
        if columns is None:
            column_selection = "*"
        else:
            cols = [col for col in columns if col != "__concat_key__"]
            column_selection = ", ".join(cols)
        return column_selection

    def _setup_test_db(self, key_sample: List[str]):
        """Re-creates a database and populates a table with key values"""
        key_values = ", ".join([f"('{key_value}')" for key_value in key_sample])
        create_statement = f"""
            DROP SCHEMA IF EXISTS __test__ CASCADE;
            CREATE SCHEMA __test__;
            CREATE TABLE __test__.__concat_keys__ (__concat_key__ STRING);
            INSERT INTO __test__.__concat_keys__ VALUES {key_values}
        """
        self.duckdb.execute(create_statement)

    def get_sample_keys(
            self, query: str, primary_keys: List[str], sample_size: int,
    ) -> List[str]:
        """See interface definition (parent class IBackend)."""

        if len(primary_keys) == 0:
            raise ValueError("Provide a non-empty list of primary keys!")

        concat_key = self._get_concat_key(primary_keys)

        random_number = randint(0, 100)
        sample_query = f"""
            {query}
            SELECT DISTINCT({concat_key}) AS __concat_key__
            FROM __expected__
            ORDER BY SHA256(CONCAT('{random_number}', __concat_key__))
            LIMIT {sample_size}
        """
        result_as_df = self.duckdb.query(sample_query).pl()
        result_as_dict = result_as_df.to_dict(as_series=False)["__concat_key__"]

        return result_as_dict

    def get_sample_from_query(
            self, query: str, primary_keys: List[str], key_sample: List[str],
            columns: Optional[List[str]] = None
    ) -> pl.DataFrame:

        if len(key_sample) == 0 or len(primary_keys) == 0:
            raise ValueError("Provide a non-empty list of primary keys and samples!")

        self._setup_test_db(key_sample=key_sample)
        concat_key = self._get_concat_key(primary_keys)
        column_selection = self._get_column_selection(columns)

        sample_query = f"""
            {query}
            SELECT __obj__.* FROM (
                SELECT {column_selection}, {concat_key} AS __concat_key__
                FROM __expected__
            ) AS __obj__
            INNER JOIN __test__.__concat_keys__ AS __keys__
                ON __obj__.__concat_key__ = __keys__.__concat_key__
        """
        result_as_df = self.duckdb.query(sample_query).pl()

        return result_as_df

    def get_sample_from_testobject(
            self, testobject: TestObjectDTO, primary_keys: List[str],
            key_sample: List[str], columns: Optional[List[str]] = None
    ) -> pl.DataFrame:

        if len(key_sample) == 0 or len(primary_keys) == 0:
            raise ValueError("Provide a non-empty list of primary keys and samples!")

        testobject_type = self.naming_resolver.get_object_type(testobject)
        if testobject_type == testobject_type.FILE:
            raise ValueError("Sampling files not yet supported")

        db = DBInstanceDTO.from_testobject(testobject)
        catalog, schema, table = self.naming_resolver.resolve_db(db, testobject.name)
        column_selection = self._get_column_selection(columns)
        self._setup_test_db(key_sample=key_sample)
        concat_key = self._get_concat_key(primary_keys)

        sample_query = f"""
            SELECT __obj__.* FROM (
                SELECT {column_selection}, {concat_key} AS __concat_key__
                FROM {catalog}.{schema}.{table}
            ) AS __obj__
            INNER JOIN __test__.__concat_keys__ AS __keys__
                ON __obj__.__concat_key__ = __keys__.__concat_key__
        """
        result_as_df = self.duckdb.query(sample_query).pl()

        return result_as_df
