from typing import List
from abc import ABC, abstractmethod

from src.dtos import (
    TestCaseResultDTO, DTO,
    TestCaseDefinitionDTO
)


class RunTestCaseCommand(DTO):
    definition: TestCaseDefinitionDTO


class IRunTestCasesCommandHandler(ABC):
    """Abstract interface to execute testcases"""

    @abstractmethod
    def run(self, commands: List[RunTestCaseCommand]) -> List[TestCaseResultDTO]:
        """Implement this method to execute testcases"""
