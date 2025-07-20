from abc import ABC, abstractmethod
from typing import List
from src.dtos import SpecificationType, TestCaseEntryDTO


class IRequirements(ABC):
    """
    Interface definition for requirements for a given testcase. Defines which
    specification types are required for a given testcase.
    """
    @abstractmethod
    def get_requirements(self, testcase: TestCaseEntryDTO) -> List[SpecificationType]:
        pass
