from src.dtos import TestCaseEntryDTO, LocationDTO, TestType
from src.specification.ports import INamingConventions, INamingConventionsFactory


class DefaultNamingConventions(INamingConventions):
    """
    Default implementation of INamingConventions for matching spec files by
    naming pattern.
    """

    def match(self, testcase: TestCaseEntryDTO, file: LocationDTO) -> bool:
        """
        Match files to testcase by testobject name and testtype. Expects .xlsx files
        for schema and .sql files for rowcount and compare sample.
        """
        testobject_ = testcase.testobject
        spec_type = testcase.testtype

        if spec_type == TestType.SCHEMA:
            conditions = [
                file.filename.startswith(f"{testobject_}_"),
                file.filename.endswith(".xlsx"),
            ]
        elif spec_type == TestType.ROWCOUNT:
            conditions = [
                file.filename.startswith(f"{testobject_}_ROWCOUNT"),
                file.filename.endswith(".sql"),
            ]
        elif spec_type == TestType.COMPARE_SAMPLE:
            conditions = [
                file.filename.startswith(f"{testobject_}_COMPARE_SAMPLE"),
                file.filename.endswith(".sql"),
            ]
        else:
            raise ValueError(f"Unsupported testtype: {spec_type}")

        return all(conditions)


class NamingConventionsFactory(INamingConventionsFactory):
    """
    Factory for NamingConventions. Perspectively each project and domain might have
    their own naming conventions. Then, this factory should be extended to return
    the appropriate naming conventions for a given domain.
    """

    def create(self, domain_name: str) -> INamingConventions:
        return DefaultNamingConventions()
