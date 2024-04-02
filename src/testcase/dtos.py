from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from typing import Union, List, Dict


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


@dataclass
class SpecificationDTO:
    type: str
    content: Union[str, dict]
    location: str
    valid: Union[bool, None] = None

    @classmethod
    def from_dict(cls, spec_as_dict: dict) -> SpecificationDTO:
        return cls(
            type=spec_as_dict["type"],
            content=spec_as_dict["content"],
            location=spec_as_dict["location"],
            valid=spec_as_dict["valid"]
        )

    def dict(self) -> dict:
        return dict(
            type=self.type,
            content=self.content,
            location=self.location,
            valid=str(self.valid)
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


@dataclass
class DomainConfigDTO:
    """
    This serves as a generic data container for business-related configurations.
    The required attributes are defined by configuration needs of implemented Testcases,
    e.g., the testcase compare_sample requires a sample size definition.
    """
    domain: str
    compare_sample_default_sample_size: int
    compare_sample_sample_size_per_object: Dict[str, int]

    @classmethod
    def from_dict(cls, domain_config_dict: dict) -> DomainConfigDTO:
        return cls(
            domain=domain_config_dict["domain"],
            compare_sample_default_sample_size=domain_config_dict[
                "compare_sample_default_sample_size"],
            compare_sample_sample_size_per_object=domain_config_dict[
                "compare_sample_sample_size_per_object"
            ]
        )
