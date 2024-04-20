from __future__ import annotations
from enum import Enum
from typing import Union, List, Dict
from src.dtos import DTO
from src.dtos.specifications import SpecificationDTO


class TestObjectDTO(DTO):
    """Unambigiusly identifies the testobject (e.g. table) to be tested"""
    __test__ = False  # prevents pytest collection
    name: str
    domain: str
    stage: str
    instance: str

    @classmethod
    def from_dict(cls, testobject_as_dict: dict) -> TestObjectDTO:
        return super().from_dict(testobject_as_dict)


class DBInstanceDTO(DTO):
    """Unambiguously identifies the database to be tested."""
    domain: str
    stage: str
    instance: str

    @classmethod
    def from_dict(cls, db_as_dict: dict) -> DBInstanceDTO:
        return super().from_dict(db_as_dict)

    @classmethod
    def from_testobject(cls, testobject: TestObjectDTO) -> DBInstanceDTO:
        return cls(
            domain=testobject.domain,
            stage=testobject.stage,
            instance=testobject.instance
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

    def to_string(self) -> str:
        return str(self.value)


class TestResult(Enum):
    __test__ = False  # prevents pytest collection
    NA = "N/A"
    OK = "OK"
    NOK = "NOK"

    def to_string(self) -> str:
        return str(self.value)


class TestCaseResultDTO(DTO):
    __test__ = False  # prevents pytest collection
    id: str
    run_id: str
    testobject: TestObjectDTO
    testtype: str
    status: TestStatus
    result: TestResult
    diff: Dict[str, Union[List, Dict]]  # found diff as a table in record-oriented dict
    summary: str
    details: List[Dict[str, Union[str, int, float]]]
    specifications: List[SpecificationDTO]
    start_ts: str
    end_ts: Union[str, None]

    def to_dict(self) -> dict:
        return dict(
            id=self.id,
            run_id=self.run_id,
            testtype=self.testtype,
            testobject=self.testobject.to_dict(),
            status=self.status.to_string(),
            summary=self.summary,
            details=self.details,
            result=self.result.to_string(),
            specifications=[spec.to_dict() for spec in self.specifications],
            start_ts=self.start_ts,
            end_ts=self.end_ts
        )
