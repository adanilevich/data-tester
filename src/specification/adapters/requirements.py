from typing import List

from src.dtos import TestCaseEntryDTO, SpecificationType, TestType
from src.specification.ports import IRequirements


class Requirements(IRequirements):
    """
    Default requirements implementation. Should only be changed in rare cases.
    """
    def get_requirements(self, testcase: TestCaseEntryDTO) -> List[SpecificationType]:
        if testcase.testtype == TestType.SCHEMA:
            return [SpecificationType.SCHEMA]
        elif testcase.testtype == TestType.ROWCOUNT:
            return [SpecificationType.ROWCOUNT_SQL]
        elif testcase.testtype == TestType.COMPARE:
            return [SpecificationType.COMPARE_SQL, SpecificationType.SCHEMA]
        else:
            raise ValueError(f"Unsupported testtype: {testcase.testtype}")
