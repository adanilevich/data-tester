from __future__ import annotations
from enum import Enum
from typing import Self, Union, List, Dict

from pydantic import Field

from src.dtos import DTO
from src.dtos.specifications import SpecificationDTO


class TestObjectDTO(DTO):
    """Unambigiusly identifies the testobject (e.g. table) to be tested"""
    __test__ = False  # prevents pytest collection
    name: str
    domain: str
    stage: str
    instance: str


class DBInstanceDTO(DTO):
    """Unambiguously identifies the database to be tested."""
    domain: str
    stage: str
    instance: str

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
    scenario: str = Field(default="")
    status: TestStatus
    result: TestResult
    diff: Dict[str, Union[List, Dict]]  # found diff as a table in record-oriented dict
    summary: str
    facts: List[Dict[str, str | int]]
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
            facts=self.facts,
            result=self.result.to_string(),
            specifications=[spec.to_dict() for spec in self.specifications],
            start_ts=self.start_ts,
            end_ts=self.end_ts
        )


class TestRunResultDTO(DTO):

    testrun_id: str
    start: str
    end: str
    result: str
    testcase_results: List[TestCaseResultDTO]

    @classmethod
    def from_testcase_results(cls, testcase_results: List[TestCaseResultDTO]) -> Self:

        result = "OK"
        for testcase_result in testcase_results:
            if testcase_result.result != "OK":
                result = "NOK"

        start = list(sorted([
            r.start_ts for r in testcase_results if r.start_ts is not None
        ]))[0]

        end = list(sorted([
            r.end_ts for r in testcase_results if r.end_ts is not None
        ], reverse=True))[0]

        testrun_id = "-".join([r.run_id for r in testcase_results])

        return cls(
            testrun_id=testrun_id,
            start=start,
            end=end,
            result=result,
            testcase_results=testcase_results,
        )
