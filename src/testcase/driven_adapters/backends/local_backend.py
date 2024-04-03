from __future__ import annotations
from typing import List, Union, Tuple, Dict, Any, Optional
from fsspec.implementations.local import LocalFileSystem  # type: ignore
import duckdb

from src.testcase.driven_ports.i_backend import IBackend
from src.testcase.dtos import DomainConfigDTO


class DemoNamingResolver:

    def __init__(self, domain_cofig: DomainConfigDTO):
        self.config = domain_cofig

    def _fetch_resolver(self, domain: str):
        if domain in ["payments, sales"]:
            return DemoDefaultResolver(domain_config=self.config)
        else:
            raise NotImplementedError(f"Resolver domain {domain} unknown!")

    def resolve_raw(self, domain: str, project: str, instance: str,
                    obj: Optional[str] = None):
        resolver = self._fetch_resolver(domain=domain)
        coordinates = resolver.resolve_raw(domain, project, instance, obj)
        return coordinates

    def resolve_db(self, domain: str, project: str, instance: str,
                   obj: Optional[str] = None):
        resolver = self._fetch_resolver(domain=domain)
        coordinates = resolver.resolve_db(domain, project, instance, obj)
        return coordinates


class DemoDefaultResolver:

    def __init__(self, domain_config: DomainConfigDTO):
        self.config: DomainConfigDTO = domain_config

    @staticmethod
    def resolve_raw(domain: str, project: str, instance: str,
                    obj: Optional[str] = None) -> str:
        """
        Returns (relative) path in raw data layer of our dummy demo DWH.
        Translates between  business coordinates and technical paths in local filesystem

        Args:
            domain: domain name - corresponds to top-level folder
            project: stage/environment - corresponds to 2nd level folder in
            instance: instance of dwh - 3rd level folder structure in local filesystem
            obj: name of testobject. If provided, full path to folder which corresponds
                to given testobject is provided, else to parent folder

        Returns:
            path: relative path in local filesystem which corresponds to specified
                business coordinates
        """

        # files are stored by <domain>/<project>/<instance>/<business object name>
        base_path = domain + "/" + project + "/" + instance + "/"
        if obj is not None:
            if not obj.startswith("raw_"):
                raise ValueError(f"Testobjects in raw_layer must start with raw_: {obj}")
            base_path += "/" + obj.removeprefix("raw_") + "/"
        return base_path

    @staticmethod
    def resolve_db(domain: str, project: str, instance: str, obj: Optional[str] = None)\
            -> Union[Tuple[str, str], Tuple[str, str, str]]:
        """
        Returns duckdb database coordinates which correspond to specified business
        coordinates of the testobject(s)

        Args:
            domain: domain name - domain_project correspond to a database in duckdb
            project: stage/environment - domain_project correspond to a database in duckdb
            instance: instance of dwh - corresponds to database schema in duckdb
            obj: name of testobject - corresponds to table or view name in duckdb

        Returns:
            (catalog, schema) or (catalog, schema, table): duckdb coordinates correspon-
                ding to business coordinates
        """
        # databases aka catalogs are organized <domain>_<project>, e.g. 'payments_test'
        # instances correspond to db schemata
        catalog = domain + "_" + project
        schema = instance
        if obj is None:
            return catalog, schema
        else:
            table = obj
            return catalog, schema, table


class DemoQueryHandler:

    def __init__(self, domain_config: DomainConfigDTO):
        self.config: DomainConfigDTO = domain_config

    def translate(self, query: str, domain: str, project, instance: str) -> str:

        translator = self._fetch_translator(domain=domain)
        translated_query = translator.translate(query, project, instance)
        return translated_query

    def _fetch_translator(self, domain: str):
        #  include any domain-specific fetching of translators here
        if domain in ["payments", "sales"]:
            return DefaultDemoTranslator(domain_config=self.config)
        else:
            raise NotImplementedError(f"Unknown translation domain f{domain}")


class DefaultDemoTranslator:

    def __init__(self, domain_config: DomainConfigDTO):
        self.config: DomainConfigDTO = domain_config

    def translate(self, query: str, project: str, instance: str) -> str:
        if self.config:
            return query + f"\n--{project}" + f"\n--{instance}"
        else:
            return query


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

    def __init__(self, raw_path: str, db_path: str, domain_config: DomainConfigDTO,
                 naming_resolver: DemoNamingResolver, query_handler: DemoQueryHandler,
                 fs: LocalFileSystem, db=duckdb):
        """
        Initialize backend.

        Args:
            raw_path: path in local file system wher raw layer of local DWH is stored
            db_path: path in local file system where all duckdb .db files are located
                on top-level
            domain_config: domain config which is used to configure handlers
            naming_resolver: resolver object which translates between business naming
                conventions for testobjects and technical coordinates
            query_handler: translates user-provided SQL queries to required stage/instance
        """

        self.raw_path: str = raw_path
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
        """See parent class."""

        # get testobjects in raw layer
        relative_raw_path = self.naming_resolver.resolve_raw(domain, project, instance)
        absolute_raw_path = self.raw_path + relative_raw_path

        raw_testobjects = []
        for obj in self.fs.ls(absolute_raw_path):
            if self.fs.isdir(obj):
                # this is actually bad - naming conventions leak into Backend!
                testobject_name = "raw_" + obj.split("/")[-1]
                raw_testobjects.append(testobject_name)

        # get testobjects from dwh / database layer
        catalog, schema = self.naming_resolver.resolve_db(domain, project, instance)
        tables_df = self.db.query(f"""
            SELECT table_name FROM INFORMATION_SCHEMA.TABLES
            WHERE table_catalog = {catalog}
            AND table_schema = {schema}
        """).pl()

        tables = tables_df.to_dict(as_series=False)["table_name"]

        return raw_testobjects + tables

    def get_rowcount(self, domain: str, project: str, instance: str,
                     testobject: str) -> int:
        """See parent class."""

        if testobject.startswith("raw_"):
            raise ValueError("Getting rowcount for file-like testobjects (e.g. raw "
                             "layer) is not supported.")
        catalog, schema, table = self.naming_resolver.resolve_db(
            domain, project, instance, testobject)

        count = self.db.query(f"""
            SELECT COUNT * AS cnt FROM {catalog}.{schema}.{table}
        """).pl().to_dict(as_series=False)["cnt"][0]

        return count

    def run_query(self, query: str, domain: str, project: str,
                  instance: str) -> Dict[str, list[Any]]:
        """See parent class."""

        translated_query = self.query_handler.translate(query, domain, project, instance)
        result = self.db.query(translated_query).pl().to_dict(as_series=False)

        return result

    def get_schema(self, domain: str, project: str, instance: str,
                   testobject: str) -> List[Dict[str, str]]:
        """
        Gets table schema from duckdb, harmonizes datatypes according to conventions and
        returns results. Schema retrieval of file objects is not supported.
        """

        if testobject.startswith("raw_"):
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
        schema_df = self.db.query(schema_query).pl()
        # convert to record-oriented dicts, e.g. list of dicts with keys 'col', 'dtype:
        schema = schema_df.to_dicts()

        harmonized_schema = [
            {item["col"]: self._harmonize_dtypes(item["dtype"])} for item in schema
        ]

        return harmonized_schema

    @staticmethod
    def _harmonize_dtypes(duckdb_dtype: str) -> str:
        """
        In our DWH project, the convention is that datatypes are relevant for comparison
        only in their simplified form, e.g. complex datatypes like ARRAY, STRUCT are
        not relevant for automated comparisons. Here, a harmonization between
        duckdb dtypes and aligned conventions take place.

        Args:
            duckdb_dtype: datatype as defined in our backend, e.g. duckdb

        Return:
            harmonized_dtype: corresponding (simplified and unified dtype) which is
                understood and refered to by data experts from business, e.g.
                    -'DECIMAL', 'NUMERIC', are translated to 'decimal'
                    - 'TEXT', 'STRING', 'VARCHAR(n)' are translated to 'string'
        """

        dtype = duckdb_dtype.lower()
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

        return harmonized_dtype
