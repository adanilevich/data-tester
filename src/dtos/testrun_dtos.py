from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Self, Union
from uuid import uuid4

from pydantic import UUID4, Field, model_validator

from src.dtos.domain_config_dtos import DomainConfigDTO
from src.dtos.dto import DTO
from src.dtos.specification_dtos import AnySpec

if TYPE_CHECKING:
    from src.dtos.testset_dtos import TestSetDTO


class TestObjectDTO(DTO):
    """Unambiguously identifies the testobject (e.g. table) to be tested"""

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


class Status(Enum):
    __test__ = False  # prevents pytest collection
    NOT_STARTED = "NOT STARTED"
    INITIATED = "INITIATED"
    ABORTED = "ABORTED"
    PRECONDITIONS = "CHECKING PRECONDITIONS"
    EXECUTING = "EXECUTING"
    ERROR = "ERROR"
    FINISHED = "FINISHED"


class Result(Enum):
    NA = "N/A"
    OK = "OK"
    NOK = "NOK"


class TestType(Enum):
    __test__ = False
    ABSTRACT = "ABSTRACT"
    SCHEMA = "SCHEMA"
    COMPARE = "COMPARE"
    ROWCOUNT = "ROWCOUNT"
    STAGECOUNT = "STAGECOUNT"
    DUMMY_OK = "DUMMY_OK"
    DUMMY_NOK = "DUMMY_NOK"
    DUMMY_EXCEPTION = "DUMMY_EXCEPTION"
    UNKNOWN = "UNKNOWN"


class TestCaseDefDTO(DTO):
    """Definition of a single testcase — input to test execution, no run-time fields."""

    __test__ = False  # prevents pytest collection
    testobject: TestObjectDTO
    testtype: TestType
    scenario: str | None = Field(default=None)
    specs: List[AnySpec]
    labels: List[str] = Field(default=[])
    testset_id: UUID4 | None = None
    testset_name: str | None = None
    domain_config: DomainConfigDTO


class TestRunDefDTO(DTO):
    """Definition of a testrun — input to test execution, no run-time fields."""

    __test__ = False  # prevents pytest collection
    testcase_defs: List[TestCaseDefDTO]
    domain: str
    stage: str
    instance: str
    domain_config: DomainConfigDTO
    labels: List[str] = Field(default=[])
    testset_id: UUID4 | None = None
    testset_name: str | None = None

    @classmethod
    def from_testset(
        cls,
        testset: TestSetDTO,
        spec_list: List[List[AnySpec]],
        domain_config: DomainConfigDTO,
    ) -> Self:
        """Creates a TestRunDefDTO from a TestSetDTO, spec list and domain config."""
        if len(spec_list) != len(testset.testcases):
            raise ValueError("spec_list must be same length as testset.testcases")

        if domain_config.domain != testset.domain:
            raise ValueError("domain_config.domain must be same as testset.domain")

        if testset.stage is None:
            raise ValueError("testset.stage must be set")

        if testset.instance is None:
            raise ValueError("testset.instance must be set")

        testcase_defs = []
        testcase_entries = list(testset.testcases.values())
        for testcase_entry, specs in zip(testcase_entries, spec_list, strict=True):
            testobject = TestObjectDTO(
                name=testcase_entry.testobject,
                domain=testset.domain,
                stage=testset.stage,
                instance=testset.instance,
            )
            testcase_def = TestCaseDefDTO(
                testobject=testobject,
                testtype=testcase_entry.testtype,
                scenario=testcase_entry.scenario,
                specs=specs,
                labels=testset.labels,
                testset_id=testset.testset_id,
                testset_name=testset.name,
                domain_config=domain_config,
            )
            testcase_defs.append(testcase_def)

        return cls(
            testcase_defs=testcase_defs,
            domain=testset.domain,
            stage=testset.stage,
            instance=testset.instance,
            domain_config=domain_config,
            labels=testset.labels,
            testset_id=testset.testset_id,
            testset_name=testset.name,
        )


class SpecEntryDTO(DTO):
    """Slim spec entry for UI discovery: specs per testobject/testtype/scenario.

    Stored in UI state keyed by domain → stage.
    Only entries with at least one non-empty spec are stored.
    """

    testobject_name: str
    testtype: TestType
    scenario: str | None = None
    specs: List[AnySpec]


class TestDTO(DTO):
    __test__ = False  # prevents pytest collection
    # reference fields
    testset_id: UUID4 = Field(default_factory=uuid4)
    # data object coordinates
    domain: str
    stage: str
    instance: str
    # dynamic data
    result: Result
    status: Status
    start_ts: datetime
    end_ts: datetime | None = None
    # user-defined data
    testset_name: str = Field(default="Testset name not set")
    labels: List[str] = Field(default=[])
    domain_config: DomainConfigDTO


class TestRunSummaryDTO(DTO):
    """Summary of testrun progress."""

    __test__ = False
    total_testcases: int = 0
    completed_testcases: int = 0
    ok_testcases: int = 0
    nok_testcases: int = 0
    na_testcases: int = 0


class TestCaseDTO(TestDTO):
    __test__ = False  # prevents pytest collection
    id: UUID4 = Field(default_factory=uuid4)
    testrun_id: UUID4 = Field(default_factory=uuid4)
    testobject: TestObjectDTO
    testtype: TestType
    scenario: str | None = Field(default=None)
    diff: Dict[str, Union[List, Dict]]  # diff as a table in record-oriented dict
    summary: str
    facts: List[Dict[str, str | int]]
    details: List[Dict[str, Union[str, int, float]]]
    specs: List[AnySpec]


class TestRunDTO(TestDTO):
    __test__ = False  # prevents pytest collection
    id: UUID4 = Field(default_factory=uuid4)
    testdefinitions: List[TestCaseDefDTO] = Field(default=[])
    results: List[TestCaseDTO] = Field(default=[])
    summary: TestRunSummaryDTO = Field(default_factory=TestRunSummaryDTO)

    @model_validator(mode="after")
    def _compute_summary(self) -> Self:
        total = len(self.testdefinitions) if self.testdefinitions else len(self.results)
        self.summary = TestRunSummaryDTO(
            total_testcases=total,
            completed_testcases=len(self.results),
            ok_testcases=sum(1 for tc in self.results if tc.result == Result.OK),
            nok_testcases=sum(1 for tc in self.results if tc.result == Result.NOK),
            na_testcases=sum(1 for tc in self.results if tc.result == Result.NA),
        )
        return self
