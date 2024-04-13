from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from typing import Union, List, Dict

from src.dtos.specifications import SpecificationDTO


@dataclass
class TestObjectDTO:
    __test__ = False  # prevents pytest collection
    name: str
    domain: str
    project: str
    instance: str

    @classmethod
    def from_dict(cls, testobject_as_dict: dict) -> TestObjectDTO:
        return cls(
            name=testobject_as_dict["name"],
            domain=testobject_as_dict["domain"],
            project=testobject_as_dict["project"],
            instance=testobject_as_dict["instance"]
        )

    def dict(self) -> dict:
        return dict(
            name=self.name,
            domain=self.domain,
            project=self.project,
            instance=self.instance
        )


class TestStatus(Enum):
    __test__ = False  # prevents pytest collection
    NOT_STARTED = "NOT STARTED"
    INITIATED = "INITIATED"
    ABORTED = "ABORTED"
    PRECONDITIONS = "CHECKING PRECONDITIONS"
    EXECUTING = "EXECUTING"
    ERROR = "ERROR"
    FINISHED = "FINISHED"

    def string(self) -> str:
        return str(self.value)


class TestResult(Enum):
    __test__ = False  # prevents pytest collection
    NA = "N/A"
    OK = "OK"
    NOK = "NOK"

    def string(self) -> str:
        return str(self.value)


@dataclass
class TestCaseResultDTO:
    __test__ = False  # prevents pytest collection
    id: str
    run_id: str
    testobject: TestObjectDTO
    testtype: str
    status: TestStatus
    result: TestResult
    diff: Dict[str, Union[List, Dict]]  # found diff as a table in record-oriented dict
    summary: str
    details: List[Dict[str, str]]
    specifications: List[SpecificationDTO]
    start_ts: str
    end_ts: Union[str, None]

    def dict(self) -> dict:
        return dict(
            id=self.id,
            run_id=self.run_id,
            testtype=self.testtype,
            testobject=self.testobject.dict(),
            status=self.status.string(),
            summary=self.summary,
            details=self.details,
            result=self.result.string(),
            specifications=[spec.dict() for spec in self.specifications],
            start_ts=self.start_ts,
            end_ts=self.end_ts
        )
