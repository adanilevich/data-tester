from __future__ import annotations

from enum import Enum

from src.dtos import DTO, DomainConfigDTO, TestObjectDTO
from src.infrastructure_ports import BackendError


class DemoNamingResolverError(BackendError):
    """
    Exception raised when a demo naming resolver operation fails.
    """


class TestobjectType(Enum):
    FILE = "FILE"  # file type testobject
    TABLE = "TABLE"  # table type testobject


class DBCoordinates(DTO):
    """Represents table coordinates in DuckDB"""

    catalog: str
    schema: str
    table: str


class DemoNamingResolver:
    def __init__(self, domain_cofig: DomainConfigDTO):
        self.config: DomainConfigDTO = domain_cofig

    @staticmethod
    def get_testobject_type(testobject: TestObjectDTO) -> TestobjectType:
        """
        Returns type of testobject, e.g. "FILE" or "TABLE" (which can also be a view).
        In our project, convention is that raw (ingest) testobjects are called
        'raw_...' (e.g. 'raw_customers') and export files are called 'export_'.
        Other than that all testobjects are tables or views.
        """
        if testobject.name.startswith("raw_") or testobject.name.startswith("export_"):
            return TestobjectType.FILE
        else:
            return TestobjectType.TABLE

    @staticmethod
    def get_testobject_name(path: str) -> str:
        """
        Returns the business-language oriented name of testobject based on
        it's storage path in the filesystem or database.

        In our demo DWH:
            For file objects:
                - '.../raw/customers/' -> 'raw_customers'
                - '.../export/customers/' -> 'export_customers'
            For db objects: CURRENTLY not supported
        """
        if len(path.split(".")) > 2:  # db-like objects domain_stage.instance.table
            return path.split("/")[-1]
        elif len(path.split("/")) > 2:  # file-like objects .../raw-or-export/folder
            base_name: str = path.split(sep="/")[-1]
            if path.split(sep="/")[-2] == "export":
                return "export_" + base_name
            elif path.split(sep="/")[-2] == "raw":
                return "raw_" + base_name
            else:
                return "raw_" + base_name
        else:
            raise ValueError(f"Unkown path {path}")

    @staticmethod
    def testobject_to_db_coordinates(testobject: TestObjectDTO) -> DBCoordinates:
        """
        Returns duckdb database coordinates (catalog, schema, table) which correspond
        to specified business testobject name and business db coordinates.
        In our demo DWH databases organized domain_stage.instance.table.
        """
        catalog: str = testobject.domain + "_" + testobject.stage
        schema: str = testobject.instance
        table: str = testobject.name
        return DBCoordinates(catalog=catalog, schema=schema, table=table)

    @staticmethod
    def get_raw_testobject(testobject: TestObjectDTO) -> TestObjectDTO:
        """Given a stage testobject, returns the raw file testobject.

        Convention: stage_X -> raw_X
        """
        raw_name: str = "raw_" + testobject.name.removeprefix("stage_")
        return TestObjectDTO(
            name=raw_name,
            domain=testobject.domain,
            stage=testobject.stage,
            instance=testobject.instance,
        )
