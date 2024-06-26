from typing import List, Self
from abc import ABC, abstractmethod
from uuid import uuid4

from pydantic import Field, UUID4

from src.dtos import (
    TestObjectDTO, TestCaseResultDTO, DomainConfigDTO, SpecificationDTO, DTO,
    SpecFactory, TestType
)


class RunTestCaseCommand(DTO):
    testobject: TestObjectDTO
    testtype: TestType
    specs: List[SpecificationDTO]
    testrun_id: UUID4 = Field(default_factory=uuid4)
    domain_config: DomainConfigDTO

    @classmethod
    def from_dict(cls, dict_: dict) -> Self:

        command = cls(
            testobject=TestObjectDTO.from_dict(dict_["testobject"]),
            testtype=dict_["testtype"],
            specs=[SpecFactory().create_from_dict(spec) for spec in dict_["specs"]],
            domain_config=DomainConfigDTO.from_dict(dict_["domain_config"]),
            testrun_id=dict_.get("testrun_id", str(uuid4())[:6]),
        )
        return command


class IRunTestCasesCommandHandler(ABC):
    """Abstract interface to execute testcases"""

    @abstractmethod
    def run(self, commands: List[RunTestCaseCommand]) -> List[TestCaseResultDTO]:
        """Implement this method to execute testcases"""
