from enum import Enum
from typing import List
from dataclasses import dataclass
from src.common_interfaces.testobject import TestObjectDTO
from src.common_interfaces.specification import SpecificationDTO


class TestStatus(Enum):
    NOT_STARTED = "NOT STARTED"
    INITIATED = "INITIATED"
    ABORTED = "ABORTED"
    PRECONDITIONS = "CHECKING PRECONDITIONS"
    EXECUTING = "EXECUTING"
    ERROR = "ERROR"
    FINISHED = "FINISHED"


class TestResult(Enum):
    NA = "N/A"
    OK = "OK"
    NOK = "NOK"


@dataclass
class TestCaseDTO:
    type: str
    testobject: TestObjectDTO
    status: TestStatus
    result: TestResult
    specifications: List[SpecificationDTO]
