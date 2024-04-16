from __future__ import annotations

from enum import Enum
from typing import Optional, Tuple, List

from src.dtos.configs import DomainConfigDTO
from src.dtos.testcase import DBInstanceDTO, TestObjectDTO


class TestobjectType(Enum):
    FILE = "FILE"  # file type testobject
    TABLE = "TABLE"  # table type testobject


class DemoNamingResolver:

    def __init__(self, domain_cofig: DomainConfigDTO):
        self.config = domain_cofig

    def _fetch_resolver(self, domain: str):
        if domain in ["payments", "sales"]:
            return DemoDefaultResolver(domain_config=self.config)
        else:
            raise NotImplementedError(f"Resolver domain {domain} unknown!")

    def get_object_type(self, testobject: TestObjectDTO) -> TestobjectType:
        resolver = self._fetch_resolver(domain=testobject.domain)
        object_type = resolver.get_object_type(testobject)
        return object_type

    def resolve_files(
            self, db: DBInstanceDTO, testobject_name: Optional[str] = None
    ) -> List[str]:
        resolver = self._fetch_resolver(domain=db.domain)
        coordinates = resolver.resolve_files(db, testobject_name)
        return coordinates

    def resolve_db(
            self, db: DBInstanceDTO, testobject_name: Optional[str] = None
    ) -> Tuple[str, str, Optional[str]]:
        resolver = self._fetch_resolver(domain=db.domain)
        coordinates = resolver.resolve_db(db, testobject_name)
        return coordinates


class DemoDefaultResolver:

    def __init__(self, domain_config: DomainConfigDTO):
        self.config: DomainConfigDTO = domain_config

    @staticmethod
    def get_object_type(testobject: TestObjectDTO):
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
    def resolve_files(
            db: DBInstanceDTO, testobject_name: Optional[str] = None
    ) -> List[str]:
        """
        Returns (relative) path in raw data layer of our dummy demo DWH.
        Translates between  business coordinates and technical paths in demo filesystem

        Args:
            db: unanbiguous identification of database to be tested
            testobject_name: name of testobject. If provided, full path to folder which
                corresponds to given testobject is provided, else to parent folder

        Returns:
            path: relative path in demo filesystem which corresponds to specified
                business coordinates
        """

        # files are stored by <domain>/<stage>/<instance>/<business object name>
        base_path = db.domain + "/" + db.stage + "/" + db.instance + "/"
        if testobject_name is not None:
            if not testobject_name.startswith("raw_"):
                msg = f"Testobjects in raw_layer must start with raw_: {testobject_name}"
                raise ValueError(msg)
            base_path += "/" + testobject_name.removeprefix("raw_") + "/"
        return [base_path]

    @staticmethod
    def resolve_db(
            db: DBInstanceDTO, testobject_name: Optional[str] = None
    ) -> Tuple[str, str, Optional[str]]:
        """
        Returns duckdb database coordinates which correspond to specified business
        coordinates of the testobject(s)

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
        catalog = db.domain + "_" + db.stage
        schema = db.instance
        return catalog, schema, testobject_name
