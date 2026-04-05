from __future__ import annotations
import threading
from typing import Dict, List, Tuple, Optional
from random import randint
from time import sleep

import duckdb
import polars as pl
from fsspec.implementations.local import LocalFileSystem

from .demo_naming_resolver import DemoNamingResolver, TestobjectType
from .demo_query_handler import DemoQueryHandler

from src.infrastructure_ports import IBackend, BackendError
from src.dtos import (
    SchemaSpecDTO,
    DomainConfigDTO,
    TestObjectDTO,
    DBInstanceDTO,
    SpecType,
    LocationDTO,
)


class DemoBackendError(BackendError):
    """
    Exception raised when a demo backend operation fails.
    """


class DemoBackend(IBackend):
    """
    Local backend: File storage is simply fixtures stored on disks. Table storage is a
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

    def __init__(
        self,
        files_path: str,
        db_path: str,
        domain_config: DomainConfigDTO,
        naming_resolver: DemoNamingResolver,
        query_handler: DemoQueryHandler,
        fs: Optional[LocalFileSystem] = None,
    ):
        """
        Initialize backend.

        Args:
            files_path: path in demo file system where file-like objects are stored,
                e.g. raw or export layers of demo DWH. Files are organized in folders:
                <files_path>/<domain>/<stage>/<instance>/<business_object>/<file>
            db_path: path in demo file system where all duckdb .db files are located
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
        self._con: Optional[duckdb.DuckDBPyConnection] = None
        self._con_lock = threading.Lock()

    @property
    def con(self) -> duckdb.DuckDBPyConnection:
        """Returns a thread-safe cursor to the shared DuckDB connection.
        The underlying connection is lazily initialized and shared; each call
        returns a new cursor so that concurrent threads do not interfere."""
        with self._con_lock:
            if self._con is None:
                self._con = duckdb.connect()
                for attempt in range(5):
                    try:
                        self._con.execute(self.attach_data_statement)
                        break
                    except duckdb.BinderException:
                        if attempt < 4:
                            sleep(0.1 * (attempt + 1))
                        else:
                            raise
        return self._con.cursor()

    @property
    def attach_data_statement(self) -> str:
        """Initialize duckdb databases from .db files in specified location"""
        statement = ""
        db_files: List[str] = [
            f for f in self.fs.ls(path=self.db_path) if f.endswith(".db")
        ]
        for db_file in db_files:
            db_name: str = db_file.split(sep="/")[-1].removesuffix(".db")
            statement += f"ATTACH IF NOT EXISTS '{db_file}' AS {db_name} (READ_ONLY);\n"
        return statement

    def get_testobjects(self, db: DBInstanceDTO) -> List[str]:
        """
        Gets both file-like testobjects (e.g. file directories in raw layer)
        and existing testobjects from db, e.g. tables and views.
        """

        # FIRST: get file-like testobjects. For that, get base paths to file like objects.
        # These could be several paths, e.g. <...>/raw and <...>/export
        rel_filepaths: List[str] = self.naming_resolver.resolve_file_object_path(db=db)
        abs_filepaths: List[str] = [self.files_path + "/" + p_ for p_ in rel_filepaths]

        file_testobjects: List[str] = []
        all_subpaths: List[str] = []
        for filepath in abs_filepaths:
            all_subpaths.extend(self.fs.ls(path=filepath))
        all_subdirs: List[str] = [path for path in all_subpaths if self.fs.isdir(path)]
        for dir in all_subdirs:
            testobject_name: str = self.naming_resolver.get_file_testobject_name(
                db=db, path=dir
            )
            file_testobjects.append(testobject_name)

        # SECOND: get testobjects from dwh / database layer
        coordinates: Tuple[str, str] = self.naming_resolver.resolve_db_schema(db=db)
        catalog: str = coordinates[0]
        schema: str = coordinates[1]
        query: str = f"""
            SELECT table_name FROM INFORMATION_SCHEMA.TABLES
            WHERE table_catalog = '{catalog}'
            AND table_schema = '{schema}'
        """
        tables_df = self.con.query(query=query).pl()
        db_testobject = tables_df.to_dict(as_series=False)["table_name"]

        return file_testobjects + db_testobject

    def get_rowcount(
        self, testobject: TestObjectDTO, filters: Optional[List[Tuple[str, str]]] = None
    ) -> int:
        """See interface definition (parent class IBackend)."""

        object_type: TestobjectType = self.naming_resolver.get_object_type(
            testobject=testobject
        )
        if object_type == object_type.FILE:
            count: int = self._get_file_rowcount(testobject=testobject, filters=filters)
        else:
            count: int = self._get_db_rowcount(testobject=testobject, filters=filters)

        return count

    def _get_db_rowcount(
        self,
        testobject: TestObjectDTO,
        filters: Optional[List[Tuple[str, str]]] = None,
    ) -> int:
        """Get rowcount of a database testobject"""

        filters_: List[Tuple[str, str]] = filters or []
        db: DBInstanceDTO = DBInstanceDTO.from_testobject(testobject)
        coordinates: Tuple[str, str, str] = self.naming_resolver.resolve_db_object(
            db=db, testobject_name=testobject.name
        )
        catalog: str = coordinates[0]
        schema: str = coordinates[1]
        table: str = coordinates[2]

        where_clause = "WHERE 1 = 1"
        for column_name, operation in filters_:
            if operation.startswith("="):
                value: str = operation.removeprefix("=")
                where_clause += f"\n\tAND {column_name} == {value}"

        query = f"""
            SELECT COUNT(*) AS __cnt__ FROM {catalog}.{schema}.{table}
            {where_clause}
        """
        count_df = self.con.query(query).pl()
        count_dict: Dict[str, List[int]] = count_df.to_dict(as_series=False)
        count: int = count_dict["__cnt__"][0]

        return count

    def _get_file_rowcount(
        self, testobject: TestObjectDTO, filters: Optional[List[Tuple[str, str]]] = None
    ) -> int:
        """Get rowcount of a file-like testobject"""

        raise DemoBackendError(
            "Getting rowcount for file-like testobjects (e.g. raw "
            "layer) is not yet supported."
        )

    def translate_query(self, query: str, db: DBInstanceDTO) -> str:
        translated_query: str = self.query_handler.translate(query, db)
        return translated_query

    def run_query(self, query: str, db: DBInstanceDTO) -> pl.DataFrame:
        """See interface definition (parent class IBackend)."""
        return self.con.query(query).pl()

    def get_schema(self, testobject: TestObjectDTO) -> SchemaSpecDTO:
        """
        Gets table schema from duckdb, harmonizes datatypes according to conventions and
        returns results. Schema retrieval of file objects is not supported.
        """

        object_type: TestobjectType = self.naming_resolver.get_object_type(testobject)
        if object_type == object_type.FILE:
            raise DemoBackendError(
                "Getting schema for file-like testobjects (e.g. raw "
                "layer) is not supported."
            )

        db: DBInstanceDTO = DBInstanceDTO.from_testobject(testobject)
        coordinates: Tuple[str, str, str] = self.naming_resolver.resolve_db_object(
            db=db, testobject_name=testobject.name
        )
        catalog: str = coordinates[0]
        schema: str = coordinates[1]
        table: str = coordinates[2]

        schema_query: str = f"""
                SELECT column_name AS col, data_type AS dtype
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE table_catalog = '{catalog}'
                AND table_schema = '{schema}'
                AND table_name = '{table}'
            """
        schema_as_df = self.con.query(schema_query).pl()
        # convert to dict with keys 'col', 'dtype' and value-lists as values
        schema_as_named_dict: Dict[str, List[str]] = schema_as_df.to_dict(as_series=False)
        # convert to a dict with column names as keys and dtypes as values
        schema_as_dict: Dict[str, str] = dict(
            zip(schema_as_named_dict["col"], schema_as_named_dict["dtype"], strict=False)
        )

        location: LocationDTO = LocationDTO(
            path=f"duckdb://{testobject.domain}_{testobject.stage}"
            f".{testobject.instance}.{testobject.name}.duck"
        )
        result = SchemaSpecDTO(
            location=location,
            columns=schema_as_dict,
            testobject=testobject.name,
            spec_type=SpecType.SCHEMA,
        )

        return result

    def get_schema_from_query(
        self, query: str, db: DBInstanceDTO
    ) -> SchemaSpecDTO:
        """Gets schema of query. Expects query to be already translated"""

        query: str = f"""
            DROP TABLE IF EXISTS __query__;
            CREATE TEMP TABLE __query__ AS (
                {query}
                SELECT * FROM __expected__
            );
            SELECT column_name as col, data_type as dtype
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE table_name = '__query__'
        """
        schema_as_df = self.con.query(query).pl()
        schema_as_named_dict: Dict[str, List[str]] = schema_as_df.to_dict(as_series=False)
        schema_as_dict: Dict[str, str] = dict[str, str](
            zip(schema_as_named_dict["col"], schema_as_named_dict["dtype"], strict=False)
        )

        location= LocationDTO(
            path=f"duckdb://{db.domain}_{db.stage}.{db.instance}.user_query.duck"
        )
        result = SchemaSpecDTO(
            location=location,
            testobject="user query",
            columns=schema_as_dict,
            spec_type=SpecType.SCHEMA,
        )

        return result

    def harmonize_schema(self, schema: SchemaSpecDTO) -> SchemaSpecDTO:
        """
        In our DWH stage, the convention is that datatypes are relevant for comparison
        only in their simplified form, e.g. complex datatypes like ARRAY, STRUCT are
        not relevant for automated comparisons. Here, a harmonization between
        duckdb dtypes and aligned conventions take place.

        Args:
            schema: original duckdb schema as list of dicts with keys 'col', 'dtype

        Return:
            schema: corresponding (simplified and unified) schema which is
                understood and refered to by fixtures experts from business, e.g.
                    -'DECIMAL', 'NUMERIC', are translated to 'decimal'
                    - 'TEXT', 'STRING', 'VARCHAR(n)' are translated to 'string'
        """

        assert schema.columns is not None  # caller provides populated schema
        harmonized_columns: Dict[str, str] = {}
        for column_name, dtype in schema.columns.items():
            dtype: str = dtype.lower()
            complex_dtypes: List[str] = ["array", "list", "interval", "struct"]

            # if dtype contains one of the complex dtype keywords, we return it as is
            # reason is that comparisons with complex dtypes are not supported
            if any([complex_dtype in dtype for complex_dtype in complex_dtypes]):
                harmonized_dtype: str = dtype
            elif "int" in dtype:
                harmonized_dtype: str = "int"
            elif "date" in dtype:
                harmonized_dtype: str = "date"
            elif "timestamp" in dtype:
                harmonized_dtype: str = "timestamp"
            elif "string" in dtype or "text" in dtype or "char" in dtype:
                harmonized_dtype: str = "string"
            elif "numeric" in dtype or "decimal" in dtype:
                harmonized_dtype: str = "decimal"
            elif "float" in dtype or "real" in dtype or "double" in dtype:
                harmonized_dtype: str = "float"
            else:
                harmonized_dtype: str = dtype

            harmonized_columns.update({column_name: harmonized_dtype})

        harmonized_schema_dto: SchemaSpecDTO = schema.copy()
        harmonized_schema_dto.columns: Dict[str, str] = harmonized_columns

        return harmonized_schema_dto

    @staticmethod
    def _get_concat_key(
        primary_keys: List[str], cast_to: Optional[SchemaSpecDTO] = None
    ) -> str:
        if cast_to is not None:
            assert cast_to.columns is not None  # caller provides populated schema
            column_list: List[str] = [
                f"CAST(CAST({col} AS {dtype}) AS STRING)"
                for col, dtype in cast_to.columns.items()
                if col in primary_keys
            ]
        else:
            column_list: List[str] = [f"CAST({key} AS STRING)" for key in primary_keys]
        concat_key: str = ", '|', ".join(column_list)
        return f"CONCAT({concat_key})"

    @staticmethod
    def _get_column_selection(
        columns: Optional[List[str]] = None,
        cast_to: Optional[SchemaSpecDTO] = None,
    ) -> str:
        if columns is None:
            if cast_to is None:
                cols: List[str] = ["*"]
            else:
                assert cast_to.columns is not None  # caller provides populated schema
                cols: List[str] = [
                    f"CAST({col} AS {dtype}) AS {col}"
                    for col, dtype in cast_to.columns.items()
                    if col != "__concat_key__"
                ]
        else:
            if cast_to is None:
                cols: List[str] = [col for col in columns if col != "__concat_key__"]
            else:
                assert cast_to.columns is not None  # caller provides populated schema
                cols: List[str] = [
                    f"CAST({col} AS {cast_to.columns[col]}) AS {col}"
                    for col in columns
                    if col in cast_to.columns and col != "__concat_key__"
                ]

        column_selection: str = ", ".join(cols)
        return column_selection

    def _setup_test_db_statement(self, key_sample: List[str]) -> str:
        """SQL statement to re-create a database, populate a table with key values"""
        key_values: str = ", ".join([f"('{key_value}')" for key_value in key_sample])
        statement = f"""
            DROP SCHEMA IF EXISTS __test__ CASCADE;
            CREATE SCHEMA __test__;
            CREATE TABLE __test__.__concat_keys__ (__concat_key__ STRING);
            INSERT INTO __test__.__concat_keys__ VALUES {key_values}
        """
        return statement

    def get_sample_keys(
        self,
        query: str,
        primary_keys: List[str],
        sample_size: int,
        db: DBInstanceDTO,
        cast_to: Optional[SchemaSpecDTO] = None,
    ) -> List[str]:
        """See interface definition (parent class IBackend)."""

        if len(primary_keys) == 0:
            raise DemoBackendError("Provide a non-empty list of primary keys!")

        concat_key: str = self._get_concat_key(primary_keys, cast_to=cast_to)

        random_number: int = randint(0, 100)
        sample_query: str = f"""
            {query}
            SELECT DISTINCT({concat_key}) AS __concat_key__
            FROM __expected__
            ORDER BY SHA256(CONCAT('{random_number}', __concat_key__))
            LIMIT {sample_size}
        """
        result_df = self.con.query(sample_query).pl()
        result_list = result_df.to_dict(as_series=False)["__concat_key__"]

        return result_list

    def get_sample_from_query(
        self,
        query: str,
        primary_keys: List[str],
        key_sample: List[str],
        db: DBInstanceDTO,
        columns: Optional[List[str]] = None,
        cast_to: Optional[SchemaSpecDTO] = None,
    ) -> pl.DataFrame:
        if len(key_sample) == 0 or len(primary_keys) == 0:
            raise DemoBackendError(
                "Provide a non-empty list of primary keys and samples!"
            )

        concat_key: str = self._get_concat_key(primary_keys, cast_to)
        column_selection: str = self._get_column_selection(columns, cast_to)

        sample_query: str = f"""
            {query}
            SELECT __obj__.* FROM (
                SELECT {column_selection}, {concat_key} AS __concat_key__
                FROM __expected__
            ) AS __obj__
            INNER JOIN __test__.__concat_keys__ AS __keys__
                ON __obj__.__concat_key__ = __keys__.__concat_key__
        """
        self.con.execute(self._setup_test_db_statement(key_sample=key_sample))
        result_as_df = self.con.query(sample_query).pl()
        return result_as_df

    def get_sample_from_testobject(
        self,
        testobject: TestObjectDTO,
        primary_keys: List[str],
        key_sample: List[str],
        columns: Optional[List[str]] = None,
        cast_to: Optional[SchemaSpecDTO] = None,
    ) -> pl.DataFrame:
        if len(key_sample) == 0 or len(primary_keys) == 0:
            raise DemoBackendError(
                "Provide a non-empty list of primary keys and samples!"
            )

        testobject_type: TestobjectType = self.naming_resolver.get_object_type(testobject)
        if testobject_type == testobject_type.FILE:
            raise DemoBackendError("Sampling files not yet supported")

        db: DBInstanceDTO = DBInstanceDTO.from_testobject(testobject)
        coordinates: Tuple[str, str, str] = self.naming_resolver.resolve_db_object(
            db=db, testobject_name=testobject.name
        )
        catalog: str = coordinates[0]
        schema: str = coordinates[1]
        table: str = coordinates[2]

        column_selection: str = self._get_column_selection(columns, cast_to)
        concat_key: str = self._get_concat_key(primary_keys, cast_to)

        sample_query: str = f"""
            SELECT __obj__.* FROM (
                SELECT {column_selection}, {concat_key} AS __concat_key__
                FROM {catalog}.{schema}.{table}
            ) AS __obj__
            INNER JOIN __test__.__concat_keys__ AS __keys__
                ON __obj__.__concat_key__ = __keys__.__concat_key__
        """
        self.con.execute(self._setup_test_db_statement(key_sample=key_sample))
        result_as_df = self.con.query(sample_query).pl()
        return result_as_df
