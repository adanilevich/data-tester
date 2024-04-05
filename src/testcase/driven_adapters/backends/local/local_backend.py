from __future__ import annotations

from typing import List, Dict, Any, Tuple, Optional

import duckdb
from fsspec.implementations.local import LocalFileSystem  # type: ignore

from src.testcase.driven_adapters.backends.local.demo_naming_resolver import (
    DemoNamingResolver)
from src.testcase.driven_adapters.backends.local.demo_query_handler import (
    DemoQueryHandler)
from src.testcase.driven_ports.i_backend import IBackend, SchemaDTO, ColumnDTO
from src.testcase.dtos import DomainConfigDTO


class LocalBackend(IBackend):
    """
    Local backend for interacting with local storage. File storage is simply data
    stored on disks. Table storage is a duckdb-based DWH. This backend is implemented
    mainly for demo purpose and purpose of integration tests.

    For resolving business naming conventions to technical paths (e.g. db names),
    a NamingResolver needs to be provided, which is used by almost all methods
    which operate on 'domain', 'project' or 'instance' keywords in their signature.

    For translating test queries provided by business to different instances and stages
    (projects) of database, a QueryHandler must be provided.
    """

    supports_db_comparison: bool = False

    def __init__(self, files_path: str, db_path: str, domain_config: DomainConfigDTO,
                 naming_resolver: DemoNamingResolver, query_handler: DemoQueryHandler,
                 fs: LocalFileSystem, db=duckdb):
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
        self.fs: LocalFileSystem = fs
        self.db = db

        # initialize databases
        self._init_dbs()

    def _init_dbs(self):
        """Initialize duckdb databases from .db files in specified location"""
        db_files = [f for f in self.fs.ls(self.db_path) if f.endswith(".db")]
        for db_file in db_files:
            db_name = db_file.split("/")[-1].removesuffix(".db")
            self.db.execute(f"ATTACH '{db_file}' AS {db_name}")

    def get_testobjects(self, domain: str, project: str, instance: str) -> List[str]:
        """
        Gets both file-like testobjects (e.g. file directories in raw layer)
        and existing testobjects from db, e.g. tables and views.
        """

        # FIRST: get file-like testobjects
        # For that, get base paths to file like objects - these could be several paths,
        # e.g. <base_path>/raw and <base_path>/export
        rel_filepaths: List[str] = self.naming_resolver.resolve_files(
            domain, project, instance)
        abs_filepaths = [self.files_path + path_ for path_ in rel_filepaths]

        file_testobjects: List[str] = []
        for filepath in abs_filepaths:
            for file_or_dir in self.fs.ls(filepath):
                if self.fs.isdir(file_or_dir):
                    # TODO: this is actually bad - naming conventions leak into Backend!
                    # implement a resolver function 'get_object_name' instead
                    testobject_name = "raw_" + file_or_dir.split("/")[-1]
                    file_testobjects.append(testobject_name)

        # SECOND, get testobjects from dwh / database layer
        catalog, schema = self.naming_resolver.resolve_db(domain, project, instance)
        tables_df = self.db.query(f"""
            SELECT table_name FROM INFORMATION_SCHEMA.TABLES
            WHERE table_catalog = {catalog}
            AND table_schema = {schema}
        """).pl()

        db_testobject = tables_df.to_dict(as_series=False)["table_name"]

        return file_testobjects + db_testobject

    def get_filenames(self, domain: str, project: str, instance: str, testobject: str) \
        -> List[str]:
        """See interface definition (parent class IBackend)."""

        object_type = self.naming_resolver.get_object_type(domain, testobject)

        if object_type != object_type.FILE:
            raise ValueError("Only file-like testobjects are supported")

        filepath = self.naming_resolver.resolve_files(
            domain, project, instance, testobject)

        filenames: List[str] = []
        for file_or_dir in self.fs.ls(filepath):
            if self.fs.isfile(file_or_dir):
                filename = file_or_dir.split("/")[-1]
                filenames.append(filename)

        return filenames

    def get_rowcount(self, domain: str, project: str, instance: str, testobject: str,
                     filters: Optional[List[Tuple[str, str]]] = None) -> int:
        """See interface definition (parent class IBackend)."""

        object_type = self.naming_resolver.get_object_type(domain, testobject)
        if object_type == object_type.FILE:
            count = self._get_db_rowcount(domain, project, instance, testobject, filters)
        else:
            count = self._get_file_rowcount(
                domain, project, instance, testobject, filters)

        return count

    def _get_db_rowcount(self, domain: str, project: str, instance: str, testobject: str,
                         filters: Optional[List[Tuple[str, str]]] = None,) \
            -> int:

        filters: List[Tuple[str, str]] = filters or []

        catalog, schema, table = self.naming_resolver.resolve_db(
            domain, project, instance, testobject)

        where_clause = "WHERE 1 = 1"
        for col_name, operation in filters:
            if operation.startswith("="):
                value = operation.removeprefix("=")
                where_clause += (
                    f"\n\tAND {col_name} == {value}"
                    f" FROM {catalog}.{schema}.{table}"
                )

        count_df = self.db.query(f"""
                SELECT 
                    COUNT * AS cnt FROM {catalog}.{schema}.{table}
                {where_clause}
            """).pl()

        count_dict = count_df.to_dict(as_series=False)  # dict {colname: [values]}
        count = count_dict["cnt"][0]

        return count

    def _get_file_rowcount(self, domain: str, project: str, instance: str,
                           testobject: str,
                           filters: Optional[List[Tuple[str, str]]] = None) -> int:
        raise ValueError("Getting rowcount for file-like testobjects (e.g. raw "
                         "layer) is not yet supported.")

    def run_query(self, query: str, domain: str, project: str,
                  instance: str) -> Dict[str, list[Any]]:
        """See interface definition (parent class IBackend)."""

        translated_query = self.query_handler.translate(query, domain, project, instance)
        result = self.db.query(translated_query).pl().to_dict(as_series=False)

        return result

    def get_schema(self, domain: str, project: str, instance: str,
                   testobject: str) -> SchemaDTO:
        """
        Gets table schema from duckdb, harmonizes datatypes according to conventions and
        returns results. Schema retrieval of file objects is not supported.
        """

        object_type = self.naming_resolver.get_object_type(domain, testobject)
        if object_type == object_type.FILE:
            raise ValueError("Getting schema for file-like testobjects (e.g. raw "
                             "layer) is not supported.")

        catalog, schema, table = self.naming_resolver.resolve_db(
            domain, project, instance, testobject)

        schema_query = f"""
                SELECT column_name AS col, dtype AS dtype
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE table_catalog = {catalog}
                AND table_schema = {schema}
                AND table_name = {table}
            """

        # convert to polars dataframe with columns 'col', 'dtype'
        schema_as_df = self.db.query(schema_query).pl()
        # convert to record-oriented dicts, e.g. list of dicts with keys 'col', 'dtype:
        schema_as_dict = schema_as_df.to_dicts()

        return SchemaDTO.from_dict(schema_as_dict=schema_as_dict)

    @staticmethod
    def harmonize_schema(schema: SchemaDTO) -> SchemaDTO:
        """
        In our DWH project, the convention is that datatypes are relevant for comparison
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

        harmonized_schema = SchemaDTO(columns=[])
        for column in schema.columns:
            column_name = column.name
            dtype = column.dtype.lower()
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

            harmonized_schema.columns.append(ColumnDTO(column_name, harmonized_dtype))

        return harmonized_schema
