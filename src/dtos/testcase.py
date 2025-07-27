from __future__ import annotations
from enum import Enum
from typing import Union, List, Dict, Self
from uuid import uuid4
from datetime import datetime

from pydantic import Field, UUID4

from src.dtos.dto import DTO
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


class TestDefinitionDTO(DTO):
    __test__ = False  # prevents pytest collection
    testobject: TestObjectDTO
    testtype: TestType
    scenario: str | None = Field(default=None)
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
    COMPARE = "COMPARE"
    ROWCOUNT = "ROWCOUNT"
    DUMMY_OK = "DUMMY_OK"
    DUMMY_NOK = "DUMMY_NOK"
    DUMMY_EXCEPTION = "DUMMY_EXCEPTION"
    UNKNOWN = "UNKNOWN"


class TestDTO(DTO):
    __test__ = False  # prevents pytest collection
    # reference fields
    testrun_id: UUID4 = Field(default_factory=uuid4)
    testset_id: UUID4 = Field(default_factory=uuid4)
    report_id: UUID4 | None = None
    # data object coordinates
    domain: str
    stage: str
    instance: str
    # dynamic data
    result: TestResult
    status: TestStatus
    start_ts: datetime
    end_ts: datetime | None = None
    # user-defined data
    testset_name: str = Field(default="Testset name not set")
    labels: List[str] = Field(default=[])
    domain_config: DomainConfigDTO



class TestCaseDTO(TestDTO):
    __test__ = False  # prevents pytest collection
    testcase_id: UUID4 = Field(default_factory=uuid4)
    testobject: TestObjectDTO
    testtype: TestType
    scenario: str | None = Field(default=None)
    diff: Dict[str, Union[List, Dict]]  # diff as a table in record-oriented dict
    summary: str
    facts: List[Dict[str, str | int]]
    details: List[Dict[str, Union[str, int, float]]]
    specifications: List[SpecificationDTO]


class TestRunDTO(TestDTO):
    __test__ = False  # prevents pytest collection
    testdefinitions: List[TestDefinitionDTO]
    testcase_results: List[TestCaseDTO] = Field(default=[])

    @property
    def object_id(self) -> str:
        """Object ID for storage purposes."""
        return str(self.testrun_id)

    @classmethod
    def from_testcases(cls, testcases: List[TestCaseDTO]) -> Self:

        result = TestResult.OK
        for testcase in testcases:
            if testcase.result != TestResult.OK:
                result = TestResult.NOK

        testrun_id = cls._get_testrun_id([testcase.testrun_id for testcase in testcases])
        testdefinitions = cls._get_testdefinitions(testcases)

        return cls(
            testrun_id=testrun_id,
            start_ts=min([tc.start_ts for tc in testcases]),
            end_ts=max([tc.end_ts for tc in testcases if tc.end_ts is not None]),
            result=result,
            testset_id=testcases[0].testset_id,
            labels=testcases[0].labels,
            testcase_results=testcases,
            testset_name="undefined testset",
            stage=testcases[0].testobject.stage,
            instance=testcases[0].testobject.instance,
            domain=testcases[0].domain_config.domain,
            domain_config=testcases[0].domain_config,
            status=TestStatus.FINISHED,
            testdefinitions=testdefinitions,
        )

    @staticmethod
    def _get_testrun_id(testrun_ids: List[UUID4]) -> UUID4:

        if not len(set(testrun_ids)) == 1:
            raise ValueError("All testcases must belong to same testrun_id!")

        if len(testrun_ids) == 0:
            raise ValueError("At least one testcase must be provided!")

        return testrun_ids[0]

    @staticmethod
    def _get_testdefinitions(testcases: List[TestCaseDTO]) -> List[TestDefinitionDTO]:

        definitions = []
        for testcase in testcases:
            definition = TestDefinitionDTO(
                testobject=testcase.testobject,
                testtype=testcase.testtype,
                scenario=testcase.scenario,
                specs=testcase.specifications,
                labels=testcase.labels,
                testset_id=testcase.testset_id,
                testrun_id=testcase.testrun_id,
                domain_config=testcase.domain_config,
            )
            definitions.append(definition)

        return definitions
