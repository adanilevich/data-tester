from __future__ import annotations

from enum import Enum
from typing import Optional, Union, Tuple

from src.testcase.dtos import DomainConfigDTO


class TestobjectType(Enum):
    FILE = "FILE"  # file type testobject
    TABLE = "TABLE"  # table type testobject


class DemoNamingResolver:

    def __init__(self, domain_cofig: DomainConfigDTO):
        self.config = domain_cofig

    def _fetch_resolver(self, domain: str):
        if domain in ["payments, sales"]:
            return DemoDefaultResolver(domain_config=self.config)
        else:
            raise NotImplementedError(f"Resolver domain {domain} unknown!")

    def get_object_type(self, domain: str, testobject: str) -> TestobjectType:
        resolver = self._fetch_resolver(domain=domain)
        object_type = resolver.get_object_type(testobject)
        return object_type

    def resolve_files(self, domain: str, project: str, instance: str,
                      obj: Optional[str] = None):
        resolver = self._fetch_resolver(domain=domain)
        coordinates = resolver.resolve_files(domain, project, instance, obj)
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
    def get_object_type(testobject: str):
        """
        In our project, convention is that raw (ingest) testobjects are called
        'raw_...' (e.g. 'raw_customers') and export files are called 'export_'.
        Other than that all testobjects are tables or views.
        """
        if testobject.startswith("raw_") or testobject.startswith("export_"):
            return TestobjectType.FILE
        else:
            return TestobjectType.TABLE

    @staticmethod
    def resolve_files(domain: str, project: str, instance: str,
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
    def resolve_db(domain: str, project: str, instance: str, obj: Optional[str] = None) \
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
