from enum import Enum
from dataclasses import dataclass
from typing import Any, Union, List, Dict


@dataclass
class TestObjectDTO:
    __test__ = False  # prevents pytest collection
    name: str
    domain: str
    project: str
    instance: str


@dataclass
class SpecificationDTO:
    type: str
    content: Any
    location: str
    valid: Union[bool, None] = None


class TestStatus(Enum):
    __test__ = False  # prevents pytest collection
    NOT_STARTED = "NOT STARTED"
    INITIATED = "INITIATED"
    ABORTED = "ABORTED"
    PRECONDITIONS = "CHECKING PRECONDITIONS"
    EXECUTING = "EXECUTING"
    ERROR = "ERROR"
    FINISHED = "FINISHED"


class TestResult(Enum):
    __test__ = False  # prevents pytest collection
    NA = "N/A"
    OK = "OK"
    NOK = "NOK"


@dataclass
class TestCaseResultDTO:
    __test__ = False  # prevents pytest collection
    id: str
    run_id: str
    type: str
    testobject: TestObjectDTO
    status: TestStatus
    result: TestResult
    specifications: List[SpecificationDTO]
    start_ts: str
    end_ts: Union[str, None]


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
