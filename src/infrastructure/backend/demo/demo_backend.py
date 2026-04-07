from __future__ import annotations
import csv
from typing import Dict, List, Tuple, Optional
from random import randint

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

        Each instance owns a fresh DuckDB connection with all .db files attached
        READ_ONLY. The connection is private to this backend instance — no
        sharing across threads, no cursors of a parent connection — so concurrent
        testcases cannot deadlock on DuckDB's writer lock.
        """

        self.files_path: str = files_path
        self.db_path: str = db_path
        self.config: DomainConfigDTO = domain_config
        self.naming_resolver: DemoNamingResolver = naming_resolver
        self.query_handler: DemoQueryHandler = query_handler
        self.fs: LocalFileSystem = LocalFileSystem()
        self.con: duckdb.DuckDBPyConnection = duckdb.connect()
        attach_sql = self._build_attach_statement()
        if attach_sql:
            self.con.execute(attach_sql)

    def _build_attach_statement(self) -> str:
        """Build the SQL to ATTACH all .db files in db_path as READ_ONLY."""
        statement = ""
        db_files: List[str] = [
            f for f in self.fs.ls(path=self.db_path, detail=False) if f.endswith(".db")
        ]
        for db_file in db_files:
            db_name: str = db_file.split(sep="/")[-1].removesuffix(".db")
            statement += f"ATTACH IF NOT EXISTS '{db_file}' AS {db_name} (READ_ONLY);\n"
        return statement

    def close(self) -> None:
        """Close the underlying DuckDB connection.

        Long-running applications and tests that create many backends should
        call this when done so the file handles and DuckDB session state are
        released promptly instead of waiting for garbage collection. Safe to
        call more than once and safe to call on a partially-initialised
        instance — any error is swallowed.
        """
        try:
            self.con.close()
        except Exception:
            pass

    def list_testobjects(self, db: DBInstanceDTO) -> List[TestObjectDTO]:
        """
        Gets both file-like testobjects (e.g. file directories in raw layer)
        and existing testobjects from db, e.g. tables and views.
        """
        domain, stage, instance = db.domain, db.stage, db.instance

        # FIRST: get file-like testobjects
        abs_path = "/".join([self.files_path, domain, stage, instance, ""])
        file_testobjects: List[TestObjectDTO] = []
        subdirs: List[str] = [
            p for p in self.fs.ls(path=abs_path, detail=False) if self.fs.isdir(p)
        ]
        for dir in subdirs:
            name: str = self.naming_resolver.get_testobject_name(path=dir)
            file_testobjects.append(
                TestObjectDTO(name=name, domain=domain, stage=stage, instance=instance)
            )

        # SECOND: get testobjects from dwh / database layer via information_schema
        dummy = TestObjectDTO(name="", domain=domain, stage=stage, instance=instance)
        coords = self.naming_resolver.testobject_to_db_coordinates(dummy)
        query: str = f"""
            SELECT table_catalog, table_schema, table_name
            FROM INFORMATION_SCHEMA.TABLES
            WHERE table_catalog = '{coords.catalog}'
            AND table_schema = '{coords.schema}'
        """
        tables_df = self.con.query(query=query).pl()
        tables: List[str] = tables_df.to_dict(as_series=False)["table_name"]
        db_testobjects = [
            TestObjectDTO(name=n, domain=domain, stage=stage, instance=instance)
            for n in tables
        ]

        return file_testobjects + db_testobjects

    def get_testobject_rowcount(
        self,
        testobject: TestObjectDTO,
        filters: Optional[List[Tuple[str, str]]] = None,
        encoding: Optional[str] = None,
        skip_lines: Optional[int] = None,
    ) -> int:
        """See interface definition (parent class IBackend)."""

        object_type = self.naming_resolver.get_testobject_type(testobject=testobject)
        if object_type == TestobjectType.FILE:
            count = self._get_file_rowcount(
                testobject=testobject,
                filters=filters,
                encoding=encoding,
                skip_lines=skip_lines,
            )
        else:
            count = self._get_db_rowcount(testobject=testobject, filters=filters)

        return count

    def _get_db_rowcount(
        self,
        testobject: TestObjectDTO,
        filters: Optional[List[Tuple[str, str]]] = None,
    ) -> int:
        """Get rowcount of a database testobject"""

        filters_: List[Tuple[str, str]] = filters or []
        coords = self.naming_resolver.testobject_to_db_coordinates(testobject)

        where_clause = "WHERE 1 = 1"
        for column_name, operation in filters_:
            if operation.startswith("="):
                value: str = operation.removeprefix("=")
                where_clause += f"\n\tAND {column_name} == {value}"

        query = f"""
            SELECT COUNT(*) AS __cnt__
            FROM {coords.catalog}.{coords.schema}.{coords.table}
            {where_clause}
        """
        count_df = self.con.query(query).pl()
        count_dict: Dict[str, List[int]] = count_df.to_dict(as_series=False)
        count: int = count_dict["__cnt__"][0]

        return count

    def _get_file_rowcount(
        self,
        testobject: TestObjectDTO,
        filters: Optional[List[Tuple[str, str]]] = None,
        encoding: Optional[str] = None,
        skip_lines: Optional[int] = None,
    ) -> int:
        """Get rowcount of a file-like testobject by streaming lines.

        Expects a ('filepath', '=<full_path>') entry in filters
        to identify the exact file to count.
        """
        filepath: Optional[str] = None
        for col, op in filters or []:
            if col == "filepath" and op.startswith("="):
                filepath = op.removeprefix("=")
        if not filepath:
            raise DemoBackendError("filepath filter is required for file rowcount.")

        # Strip storage type prefix (e.g. "local://")
        if "://" in filepath:
            filepath = filepath.split("://", 1)[1]

        if not self.fs.exists(filepath):
            raise DemoBackendError(f"File not found: {filepath}")

        file_encoding: str = encoding or self._infer_encoding(filepath)
        file_skip: int = (
            skip_lines
            if skip_lines is not None
            else self._infer_skip_lines(filepath, file_encoding)
        )

        line_count: int = 0
        with self.fs.open(filepath, mode="r", encoding=file_encoding) as fh:
            for _ in fh:
                line_count += 1

        return max(0, line_count - file_skip)

    def _infer_encoding(self, filepath: str) -> str:
        """Infer encoding by trying common encodings on a small sample."""
        candidates: List[str] = ["utf-8", "ascii", "latin-1", "cp1252"]
        for enc in candidates:
            try:
                with self.fs.open(filepath, mode="rb") as fh:
                    sample: bytes = fh.read(8192)
                sample.decode(enc)
                return enc
            except (UnicodeDecodeError, LookupError):
                continue
        raise DemoBackendError(
            f"Cannot infer encoding for file: {filepath}. Tried: {', '.join(candidates)}"
        )

    def _infer_skip_lines(self, filepath: str, encoding: str) -> int:
        """Infer number of header lines to skip (assumes csv-like format)."""
        with self.fs.open(filepath, mode="r", encoding=encoding) as fh:
            head_lines: List[str] = []
            for i, line in enumerate(fh):
                if i >= 20:
                    break
                head_lines.append(line)

        if len(head_lines) < 2:
            return 0

        try:
            sniffer = csv.Sniffer()
            sample: str = "".join(head_lines)
            has_header: bool = sniffer.has_header(sample)
            return 1 if has_header else 0
        except csv.Error:
            return 0

    def get_raw_testobject(self, testobject: TestObjectDTO) -> TestObjectDTO:
        """Given a stage testobject, returns the corresponding raw file testobject."""
        return self.naming_resolver.get_raw_testobject(testobject)

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

        object_type: TestobjectType = self.naming_resolver.get_testobject_type(testobject)
        if object_type == object_type.FILE:
            raise DemoBackendError(
                "Getting schema for file-like testobjects (e.g. raw "
                "layer) is not supported."
            )

        coords = self.naming_resolver.testobject_to_db_coordinates(testobject)

        schema_query: str = f"""
                SELECT column_name AS col, data_type AS dtype
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE table_catalog = '{coords.catalog}'
                AND table_schema = '{coords.schema}'
                AND table_name = '{coords.table}'
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

    def get_schema_from_query(self, query: str, db: DBInstanceDTO) -> SchemaSpecDTO:
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

        location = LocationDTO(
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
        """SQL statement to (re)create a connection-local temp table of keys.

        Uses CREATE OR REPLACE TEMP TABLE so the table lives in DuckDB's
        per-connection ``temp`` schema and cannot collide with anything in
        another DemoBackend instance.
        """
        key_values: str = ", ".join([f"('{key_value}')" for key_value in key_sample])
        statement = f"""
            CREATE OR REPLACE TEMP TABLE __concat_keys__ (__concat_key__ STRING);
            INSERT INTO __concat_keys__ VALUES {key_values}
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
            INNER JOIN __concat_keys__ AS __keys__
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

        testobject_type: TestobjectType = self.naming_resolver.get_testobject_type(
            testobject
        )
        if testobject_type == testobject_type.FILE:
            raise DemoBackendError("Sampling files not yet supported")

        coords = self.naming_resolver.testobject_to_db_coordinates(testobject)

        column_selection: str = self._get_column_selection(columns, cast_to)
        concat_key: str = self._get_concat_key(primary_keys, cast_to)

        sample_query: str = f"""
            SELECT __obj__.* FROM (
                SELECT {column_selection}, {concat_key} AS __concat_key__
                FROM {coords.catalog}.{coords.schema}.{coords.table}
            ) AS __obj__
            INNER JOIN __concat_keys__ AS __keys__
                ON __obj__.__concat_key__ = __keys__.__concat_key__
        """
        self.con.execute(self._setup_test_db_statement(key_sample=key_sample))
        result_as_df = self.con.query(sample_query).pl()
        return result_as_df
