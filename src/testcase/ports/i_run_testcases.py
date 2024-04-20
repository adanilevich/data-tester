from __future__ import annotations
from dataclasses import dataclass
from typing import List
from abc import ABC, abstractmethod

from src.dtos import TestObjectDTO, TestCaseResultDTO, DomainConfigDTO, SpecificationDTO


@dataclass
class RunTestCaseCommand:
    testobject: TestObjectDTO
    testtype: str
    specs: List[SpecificationDTO]
    domain_config: DomainConfigDTO

    @classmethod
    def from_dict(cls, command_as_dict: dict) -> RunTestCaseCommand:
        command_as_dto = cls(
            testobject=TestObjectDTO.from_dict(command_as_dict["testobject"]),
            testtype=command_as_dict["testtype"],
            specs=[SpecificationDTO.from_dict(spec) for spec in command_as_dict["specs"]],
            domain_config=DomainConfigDTO.from_dict(command_as_dict["domain_config"])
        )
        return command_as_dto


class IRunTestCasesCommandHandler(ABC):
    """Abstract interface to execute testcases"""

    @abstractmethod
    def run(self, commands: List[RunTestCaseCommand]) -> List[TestCaseResultDTO]:
        """Implement this method to execute testcases"""
