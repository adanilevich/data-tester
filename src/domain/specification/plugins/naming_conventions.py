from typing import Tuple, List

from src.dtos import TestCaseEntryDTO, LocationDTO, TestType, SpecificationType
from .i_naming_conventions import INamingConventions, INamingConventionsFactory


class SpecNamingConventionsError(Exception):
    """"""


class DefaultNamingConventions(INamingConventions):
    """
    Default implementation of INamingConventions for matching spec files by
    naming pattern.
    """

    def match(
        self, testcase: TestCaseEntryDTO, file: LocationDTO
    ) -> Tuple[bool, List[SpecificationType]]:
        """
        Match files to testcase by testobject name and testtype. Expects .xlsx files
        for schema and .sql files for rowcount and compare.
        """
        testobject_ = testcase.testobject

        schema_xlsx_naming_conditions = [
            file.filename.startswith(f"{testobject_}_"),
            file.filename.endswith(".xlsx"),
        ]
        rowcount_sql_naming_conditions = [
            file.filename.startswith(f"{testobject_}_ROWCOUNT"),
            file.filename.endswith(".sql"),
        ]
        compare_sql_naming_conditions = [
            file.filename.startswith(f"{testobject_}_COMPARE"),
            file.filename.endswith(".sql"),
        ]

        match = False
        spec_types = []
        # for schema testcase, only an .xlsx schema definition file is expected
        if testcase.testtype == TestType.SCHEMA:
            match = all(schema_xlsx_naming_conditions)
            spec_types = [SpecificationType.SCHEMA] if match else []
        # for rowcount testcase, only a .sql file is expected
        elif testcase.testtype == TestType.ROWCOUNT:
            match = all(rowcount_sql_naming_conditions)
            spec_types = [SpecificationType.ROWCOUNT_SQL] if match else []
        # for compare testcase, an .sql file and a schema defintion are expected
        elif testcase.testtype == TestType.COMPARE:
            if all(compare_sql_naming_conditions):
                match = True
                spec_types = [SpecificationType.COMPARE_SQL]
            if all(schema_xlsx_naming_conditions):
                match = True
                spec_types.append(SpecificationType.SCHEMA)
        elif testcase.testtype in [
            TestType.DUMMY_OK,
            TestType.DUMMY_NOK,
            TestType.DUMMY_EXCEPTION,
        ]:
            match = False
            spec_types = []
        else:
            raise SpecNamingConventionsError(
                f"Unsupported testtype: {testcase.testtype}"
            )

        return match, spec_types


class NamingConventionsFactory(INamingConventionsFactory):
    """
    Factory for NamingConventions. Perspectively each project and domain might have
    their own naming conventions. Then, this factory should be extended to return
    the appropriate naming conventions for a given domain.
    """

    def create(self, domain_name: str) -> INamingConventions:
        return DefaultNamingConventions()
