from abc import ABC, abstractmethod
from typing import Dict, List

from src.testcase.ports import IDataPlatform
from src.dtos import TestObjectDTO, SpecificationDTO


class ICheckable(ABC):
    """
    Defines the interface which is required by a precondition checker.
    Since precondition checkers mainly operate on TestCase objects, TestCase inherits
    from this interface.
    """

    testobject: TestObjectDTO  # checking testobject existence required testobject spec
    backend: IDataPlatform  # precondition checkers orchestrate backend methods
    required_specs: List[str] = []
    specs: List[SpecificationDTO] = []
    summary: str = ""
    details: List[Dict[str, str]] = []

    @abstractmethod
    def update_summary(self, summary: str):
        """Precondition checkers can update summary of the testcase/checkable."""

    @abstractmethod
    def add_detail(self, detail: Dict[str, str]):
        """Checkers can add execution details to checkable to be printed in report"""

    @abstractmethod
    def notify(self, message: str):
        """Checkers are free to inform users on their actions"""
