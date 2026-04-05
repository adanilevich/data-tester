from __future__ import annotations
from enum import Enum
from typing import Union, List, Dict, Self, TYPE_CHECKING
from uuid import uuid4
from datetime import datetime

from pydantic import Field, UUID4

from src.dtos.dto import DTO
from src.dtos.domain_config_dtos import DomainConfigDTO
from src.dtos.specification_dtos import SpecDTO

if TYPE_CHECKING:
    from src.dtos.testset_dtos import TestSetDTO


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
            domain=testobject.domain, stage=testobject.stage, instance=testobject.instance
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
    specs: List[SpecDTO]
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
    specifications: List[SpecDTO]


class TestRunSummaryDTO(DTO):
    """Summary of testrun progress — updated after each testcase completes."""
    __test__ = False
    total_testcases: int = 0
    completed_testcases: int = 0
    ok_testcases: int = 0
    nok_testcases: int = 0
    na_testcases: int = 0


class TestRunDTO(TestDTO):
    __test__ = False  # prevents pytest collection
    testdefinitions: List[TestDefinitionDTO]
    testcase_results: List[TestCaseDTO] = Field(default=[])
    summary: TestRunSummaryDTO = Field(default_factory=TestRunSummaryDTO)

    @property
    def object_id(self) -> str:
        """Object ID for storage purposes."""
        return str(self.testrun_id)

    @classmethod
    def from_testset(
        cls,
        testset: TestSetDTO,
        spec_list: List[List[SpecDTO]],
        domain_config: DomainConfigDTO
    ) -> Self:
        """
        Creates a TestRunDTO from a TestSetDTO, a list of specifications and a
        domain config.
        """

        if len(spec_list) != len(testset.testcases):
            raise ValueError("spec_list must be same length as testset.testcases")

        if domain_config.domain != testset.domain:
            raise ValueError("domain_config.domain must be same as testset.domain")

        if testset.stage is None:
            raise ValueError("testset.stage must be set")

        if testset.instance is None:
            raise ValueError("testset.instance must be set")

        testrun_id = uuid4()
        testdefinitions = []

        testcase_entries = list(testset.testcases.values())
        for testcase_entry, specs in zip(testcase_entries, spec_list, strict=True):
            testobject = TestObjectDTO(
                name=testcase_entry.testobject,
                domain=testset.domain,
                stage=testset.stage,
                instance=testset.instance
            )

            definition = TestDefinitionDTO(
                testobject=testobject,
                testtype=testcase_entry.testtype,
                scenario=testcase_entry.scenario,
                specs=specs,
                labels=testset.labels,
                testset_id=testset.testset_id,
                testrun_id=testrun_id,
                domain_config=domain_config
            )
            testdefinitions.append(definition)

        return cls(
            testrun_id=testrun_id,
            testset_id=testset.testset_id,
            testset_name=testset.name,
            labels=testset.labels,
            domain=testset.domain,
            stage=testset.stage,
            instance=testset.instance,
            start_ts=datetime.now(),
            end_ts=None,
            result=TestResult.NA,
            status=TestStatus.NOT_STARTED,
            testdefinitions=testdefinitions,
            testcase_results=[],
            domain_config=domain_config,
            summary=TestRunSummaryDTO(total_testcases=len(testdefinitions)),
        )

    @classmethod
    def from_testcases(cls, testcases: List[TestCaseDTO]) -> Self:
        result = TestResult.OK
        if all([tc.result == TestResult.OK for tc in testcases]):
            result = TestResult.OK
        elif any([tc.result == TestResult.NOK for tc in testcases]):
            result = TestResult.NOK
        else:
            result = TestResult.NA

        testrun_id = cls._get_testrun_id([testcase.testrun_id for testcase in testcases])
        testdefinitions = cls._get_testdefinitions(testcases)

        if all([tc.end_ts is None for tc in testcases]):
            end_ts = datetime.now()
        else:
            end_ts = max([tc.end_ts for tc in testcases if tc.end_ts is not None])

        summary = TestRunSummaryDTO(
            total_testcases=len(testcases),
            completed_testcases=len(testcases),
            ok_testcases=sum(1 for tc in testcases if tc.result == TestResult.OK),
            nok_testcases=sum(1 for tc in testcases if tc.result == TestResult.NOK),
            na_testcases=sum(1 for tc in testcases if tc.result == TestResult.NA),
        )

        return cls(
            testrun_id=testrun_id,
            start_ts=min([tc.start_ts for tc in testcases]),
            end_ts=end_ts,
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
            summary=summary,
        )

    @staticmethod
    def _get_testrun_id(testrun_ids: List[UUID4]) -> UUID4:
        number_of_different_testrun_ids = len(set(testrun_ids))
        if number_of_different_testrun_ids == 0:
            raise ValueError("At least one testcase must be provided!")
        elif number_of_different_testrun_ids > 1:
            raise ValueError("All testcases must belong to same testrun_id!")

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
