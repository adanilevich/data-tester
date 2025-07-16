from uuid import uuid4
from typing import List

from pydantic import Field
from pydantic import UUID4

from src.dtos.dto import DTO
from src.dtos.testcase import TestType


class TestCaseEntryDTO(DTO):
    __test__ = False  # prevents pytest collection
    testobject: str
    testtype: TestType
    comment: str = Field(default="")


class TestSetDTO(DTO):
    __test__ = False  # prevents pytest collection
    testset_id: UUID4 = Field(default_factory=uuid4)
    name: str
    description: str = Field(default="")
    labels: List[str] = Field(default=[])
    domain: str
    default_stage: str  # default stage. not necessarily where testset is executed
    default_instance: str  # default instance. not necessarily where testset is executed
    testcases: List[TestCaseEntryDTO]
