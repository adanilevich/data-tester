from src.dtos import TestCaseEntryDTO, LocationDTO, TestType
from .i_naming_conventions import INamingConventions, INamingConventionsFactory


class DefaultNamingConventions(INamingConventions):
    """
    Default implementation of INamingConventions for matching spec files by
    naming pattern.
    """

    def match(self, testcase: TestCaseEntryDTO, file: LocationDTO) -> bool:
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

        # for schema testcase, only an .xlsx schema definition file is expected
        if testcase.testtype == TestType.SCHEMA:
            result = all(schema_xlsx_naming_conditions)
        # for rowcount testcase, only a .sql file is expected
        elif testcase.testtype == TestType.ROWCOUNT:
            result = all(rowcount_sql_naming_conditions)
        # for compare testcase, an .sql file and a schema defintion are expected
        elif testcase.testtype == TestType.COMPARE:
            result = any(
                [all(compare_sql_naming_conditions), all(schema_xlsx_naming_conditions)]
            )
        else:
            raise ValueError(f"Unsupported testtype: {testcase.testtype}")

        return result


class NamingConventionsFactory(INamingConventionsFactory):
    """
    Factory for NamingConventions. Perspectively each project and domain might have
    their own naming conventions. Then, this factory should be extended to return
    the appropriate naming conventions for a given domain.
    """

    def create(self, domain_name: str) -> INamingConventions:
        return DefaultNamingConventions()
