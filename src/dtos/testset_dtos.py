from datetime import datetime
from typing import Dict, List
from uuid import uuid4

from pydantic import UUID4, Field, computed_field

from src.dtos.dto import DTO
from src.dtos.testrun_dtos import TestType


class TestCaseEntryDTO(DTO):
    __test__ = False  # prevents pytest collection
    domain: str
    testobject: str
    testtype: TestType
    scenario: str | None = Field(default=None)
    comment: str = Field(default="")

    @computed_field
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
    stage: str | None = None  # stage where testset is executed
    instance: str | None = None  # Exectution instance
    testcases: Dict[str, TestCaseEntryDTO]  # dict by identifier
    comment: str = Field(default="")

    def model_post_init(self, __context):
        if self.stage is None:
            self.stage = self.default_stage
        if self.instance is None:
            self.instance = self.default_instance

    @property
    def id(self) -> str:
        return str(self.testset_id)

    last_updated: datetime = Field(default_factory=datetime.now)
