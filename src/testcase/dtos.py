from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
from typing import Union, List, Dict, Optional, Any


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


@dataclass
class SchemaTestCaseConfigDTO:
    compare_data_types: List[str]

    @classmethod
    def from_dict(cls, config_as_dicf: Dict[str, List[str]]):
        return cls(compare_data_types=config_as_dicf["compare_data_types"])


@dataclass
class CompareSampleTestCaseConfigDTO:
    sample_size: int
    sample_size_per_object: Optional[Dict[str, int]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, config_as_dict: Dict[str, Any]):
        specified_sample_size_per_object: Optional[Dict] = config_as_dict.get(
            "sample_size_per_object", None)
        if specified_sample_size_per_object is None:
            sample_size_per_object: dict = dict()
        elif len(specified_sample_size_per_object) == 0:
            sample_size_per_object = dict()
        else:
            sample_size_per_object = specified_sample_size_per_object

        return cls(
            sample_size=config_as_dict["sample_size"],
            sample_size_per_object=sample_size_per_object
        )


@dataclass
class DomainConfigDTO:
    """
    This serves as a generic data container for business-related configurations.
    The required attributes are defined by configuration needs of implemented Testcases,
    e.g., the testcase compare_sample requires a sample size definition.
    """
    domain: str
    schema_testcase_config: SchemaTestCaseConfigDTO
    compare_sample_testcase_config: CompareSampleTestCaseConfigDTO

    @classmethod
    def from_dict(cls, domain_config_dict: dict) -> DomainConfigDTO:
        return cls(
            domain=domain_config_dict["domain"],
            schema_testcase_config=SchemaTestCaseConfigDTO.from_dict(
                domain_config_dict["schema_testcase_config"]),
            compare_sample_testcase_config=CompareSampleTestCaseConfigDTO.from_dict(
                domain_config_dict["compare_sample_testcase_config"]
            )
        )
