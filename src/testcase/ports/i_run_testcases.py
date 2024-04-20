from typing import List, Self
from abc import ABC, abstractmethod
from uuid import uuid4

from pydantic import Field

from src.dtos import (
    TestObjectDTO, TestCaseResultDTO, DomainConfigDTO, SpecificationDTO, DTO,
    SpecFactory
)


class RunTestCaseCommand(DTO):
    testobject: TestObjectDTO
    testtype: str
    specs: List[SpecificationDTO]
    run_id: str = Field(default_factory=lambda: str(uuid4())[:6])
    domain_config: DomainConfigDTO

    @classmethod
    def from_dict(cls, dict_: dict) -> Self:

        command = cls(
            testobject=TestObjectDTO.from_dict(dict_["testobject"]),
            testtype=dict_["testtype"],
            specs=[SpecFactory().create_from_dict(spec) for spec in dict_["specs"]],
            domain_config=DomainConfigDTO.from_dict(dict_["domain_config"]),
            run_id=dict_.get("run_id", str(uuid4())[:6]),
        )
        return command


class IRunTestCasesCommandHandler(ABC):
    """Abstract interface to execute testcases"""

    @abstractmethod
    def run(self, commands: List[RunTestCaseCommand]) -> List[TestCaseResultDTO]:
        """Implement this method to execute testcases"""
