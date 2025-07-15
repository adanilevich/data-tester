from __future__ import annotations
from enum import Enum
from typing import Self, Union, List, Dict
from uuid import uuid4
from datetime import datetime

from pydantic import Field, UUID4

from src.dtos import DTO
from src.dtos.domain_config import DomainConfigDTO
from src.dtos.specification import SpecificationDTO


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


class TestCaseDefinitionDTO(DTO):
    __test__ = False  # prevents pytest collection
    testobject: TestObjectDTO
    testtype: TestType
    specs: List[SpecificationDTO]
    labels: List[str] = Field(default=[])
    testset_id: UUID4 = Field(default_factory=uuid4)
    testrun_id: UUID4 = Field(default_factory=uuid4)
    domain_config: DomainConfigDTO


class TestResult(Enum):
    __test__ = False  # prevents pytest collection
    NA = "N/A"
    OK = "OK"
    NOK = "NOK"


class TestType(Enum):
    __test__ = False
    ABSTRACT = "ABSTRACT"
    SCHEMA = "SCHEMA"
    COMPARE_SAMPLE = "COMPARE_SAMPLE"
    ROWCOUNT = "ROWCOUNT"
    DUMMY_OK = "DUMMY_OK"
    DUMMY_NOK = "DUMMY_NOK"
    DUMMY_EXCEPTION = "DUMMY_EXCEPTION"
    UNKNOWN = "UNKNOWN"


class TestResultDTO(DTO):
    __test__ = False  # prevents pytest collection
    testrun_id: UUID4 = Field(default_factory=uuid4)
    testset_id: UUID4 = Field(default_factory=uuid4)
    labels: List[str] = Field(default=[])
    report_id: UUID4 | None = None
    start_ts: datetime
    end_ts: datetime
    result: TestResult


class TestCaseResultDTO(TestResultDTO):
    __test__ = False  # prevents pytest collection
    testcase_id: UUID4 = Field(default_factory=uuid4)
    testobject: TestObjectDTO
    testtype: TestType
    status: TestStatus
    diff: Dict[str, Union[List, Dict]]  # diff as a table in record-oriented dict
    summary: str
    facts: List[Dict[str, str | int]]
    details: List[Dict[str, Union[str, int, float]]]
    specifications: List[SpecificationDTO]


class TestRunResultDTO(TestResultDTO):
    __test__ = False  # prevents pytest collection
    testcase_results: List[TestCaseResultDTO]

    @classmethod
    def from_testcase_results(cls, testcase_results: List[TestCaseResultDTO]) -> Self:

        result = TestResult.OK
        for testcase_result in testcase_results:
            if testcase_result.result != TestResult.OK:
                result = TestResult.NOK

        start_ts = min([res.start_ts for res in testcase_results])
        end_ts = max([res.end_ts for res in testcase_results])
        testrun_id = cls._get_testrun_id([res.testrun_id for res in testcase_results])
        return cls(
            testrun_id=testrun_id,
            start_ts=start_ts,
            end_ts=end_ts,
            result=result,
            testset_id=testcase_results[0].testset_id,
            labels=testcase_results[0].labels,
            testcase_results=testcase_results,
        )

    @staticmethod
    def _get_testrun_id(testrun_ids: List[UUID4]) -> UUID4:

        if not len(set(testrun_ids)) == 1:
            raise ValueError("All testcases must belong to same testrun_id!")

        if len(testrun_ids) == 0:
            raise ValueError("At least one testcase must be provided!")

        return testrun_ids[0]
