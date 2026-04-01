from __future__ import annotations
from enum import Enum
from typing import Tuple, List

from src.dtos import DomainConfigDTO, DBInstanceDTO, TestObjectDTO
from src.infrastructure_ports import BackendError


class DemoNamingResolverError(BackendError):
    """
    Exception raised when a demo naming resolver operation fails.
    """


class TestobjectType(Enum):
    FILE = "FILE"  # file type testobject
    TABLE = "TABLE"  # table type testobject


class DemoNamingResolver:
    def __init__(self, domain_cofig: DomainConfigDTO):
        self.config: DomainConfigDTO = domain_cofig

    def _fetch_resolver(self, domain: str) -> DemoDefaultResolver:
        if domain in ["payments", "sales"]:
            return DemoDefaultResolver(domain_config=self.config)
        else:
            raise DemoNamingResolverError(f"Resolver domain {domain} unknown!")

    def get_object_type(self, testobject: TestObjectDTO) -> TestobjectType:
        resolver: DemoDefaultResolver = self._fetch_resolver(domain=testobject.domain)
        object_type: TestobjectType = resolver.get_object_type(testobject)
        return object_type

    def resolve_file_object_path(self, db: DBInstanceDTO) -> List[str]:
        resolver: DemoDefaultResolver = self._fetch_resolver(domain=db.domain)
        coordinates: list[str] = resolver.resolve_file_object_path(db)
        return coordinates

    def get_file_testobject_name(self, db: DBInstanceDTO, path: str) -> str:
        resolver: DemoDefaultResolver = self._fetch_resolver(domain=db.domain)
        testobject_name: str = resolver.get_file_testobject_name(path=path)
        return testobject_name

    def resolve_db_object(
        self, db: DBInstanceDTO, testobject_name: str
    ) -> Tuple[str, str, str]:
        resolver: DemoDefaultResolver = self._fetch_resolver(domain=db.domain)
        coordinates: Tuple[str, str, str] = resolver.resolve_db_object(
            db=db, testobject_name=testobject_name
        )
        return coordinates

    def resolve_db_schema(self, db: DBInstanceDTO) -> Tuple[str, str]:
        resolver: DemoDefaultResolver = self._fetch_resolver(domain=db.domain)
        coordinates: Tuple[str, str] = resolver.resolve_db_schema(db=db)
        return coordinates


class DemoDefaultResolver:
    def __init__(self, domain_config: DomainConfigDTO):
        self.config: DomainConfigDTO = domain_config

    @staticmethod
    def get_object_type(testobject: TestObjectDTO) -> TestobjectType:
        """
        In our project, convention is that raw (ingest) testobjects are called
        'raw_...' (e.g. 'raw_customers') and export files are called 'export_'.
        Other than that all testobjects are tables or views.
        """
        if testobject.name.startswith("raw_") or testobject.name.startswith("export_"):
            return TestobjectType.FILE
        else:
            return TestobjectType.TABLE

    @staticmethod
    def resolve_file_object_path(db: DBInstanceDTO) -> List[str]:
        """
        Returns (relative) path in raw fixtures layer of our dummy demo DWH.
        Translates between  business coordinates and technical paths in demo filesystem

        Args:
            db: unanbiguous identification of database to be tested

        Returns:
            path: relative path to a folder in demo filesystem which corresponds to
            specified business coordinates
        """

        # files are stored by <domain>/<stage>/<instance>/<business object name>/<file>
        base_path: str = db.domain + "/" + db.stage + "/" + db.instance + "/"
        return [base_path]

    @staticmethod
    def get_file_testobject_name(path: str) -> str:
        """
        Returns the business-language oriented name of a file-like testobject based on
        it's storage path in the filesystem, e.g. if the storage path is
        '.../raw/customers/' then 'raw_customers' is returned, for
        '.../export/customers/', 'export_customers' is returned

        Args:
            path: full path in filesystem, e.g.
            <base_path>/<domain>/<stage>/<instance>/<layer>/<business_object_name>/
            here <layer> is 'raw' or 'export' and is optional (then interpreted as 'raw')

        Returns:
            testobject_name: see base docstring
        """
        base_name: str = path.split(sep="/")[-1]
        if path.split(sep="/")[-2] == 'export':
            return 'export_' + base_name
        elif path.split(sep="/")[-2] == 'raw':
            return 'raw_' + base_name
        else:
            return 'raw_' + base_name

    @staticmethod
    def resolve_db_object(
        db: DBInstanceDTO, testobject_name: str
    ) -> Tuple[str, str, str]:
        """
        Returns duckdb database coordinates which correspond to specified business
        coordinates of the testobject

        Args:
            db: unanbiguous identification of database to be tested
            testobject_name: name of testobject - corresponds to table or view name
                in duckdb

        Returns:
            (catalog, schema) or (catalog, schema, table): duckdb coordinates correspon-
                ding to business coordinates
        """
        # databases aka catalogs are organized <domain>_<stage>, e.g. 'payments_test'
        # instances correspond to db schemata
        catalog: str = db.domain + "_" + db.stage
        schema: str = db.instance
        table: str = testobject_name
        return catalog, schema, table

    @staticmethod
    def resolve_db_schema(db: DBInstanceDTO) -> Tuple[str, str]:
        catalog: str = db.domain + "_" + db.stage
        schema: str = db.instance
        return catalog, schema
