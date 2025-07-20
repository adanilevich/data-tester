from uuid import uuid4
from typing import List, Dict
from datetime import datetime

from pydantic import Field, computed_field
from pydantic import UUID4

from src.dtos.dto import DTO
from src.dtos.testcase import TestType


class TestCaseEntryDTO(DTO):
    __test__ = False  # prevents pytest collection
    testobject: str
    testtype: TestType
    scenario: str | None = Field(default=None)
    comment: str = Field(default="")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(self) -> str:
        res = f"{self.testobject}_{self.testtype.value}"
        if self.scenario:
            res += f"_{self.scenario}"
        return res


class TestSetDTO(DTO):
    __test__ = False  # prevents pytest collection
    testset_id: UUID4 = Field(default_factory=uuid4)
    name: str
    description: str = Field(default="")
    labels: List[str] = Field(default=[])
    domain: str
    default_stage: str  # default stage. not necessarily where testset is executed
    default_instance: str  # default instance. not necessarily where testset is executed
    testcases: Dict[str, TestCaseEntryDTO]  # dict by identifier
    last_updated: datetime = Field(default_factory=datetime.now)
