from abc import ABC, abstractmethod
from typing import Dict
from src.testcase.dtos import TestObjectDTO
from src.testcase.driven_ports.backend_interface import IBackend


class AbstractCheckable(ABC):
    """
    Defines the interface which is required by a precondition checker.
    Since precondition checkers mainly operate on TestCase objects, TestCase inherits
    from this interface
    """

    testobject: TestObjectDTO  # checking testobject existence required testobject spec
    backend: IBackend  # precondition checkers orchestrate backend methods

    @abstractmethod
    def update_summary(self, summary: str):
        """Precondition checkers can update summary of the testcase/checkable."""
        raise (NotImplementedError("Implement update_summary for your checkable"))

    @abstractmethod
    def add_detail(self, detail: Dict[str, str]):
        """Precondition checkers add testcase executino details to be printed in report"""
        raise (NotImplementedError("Implement add_detail for your checkable"))

    @abstractmethod
    def notify(self, message: str):
        """Precondition checkers are free to inform users on their actions"""
        raise (NotImplementedError("Implement notify for your checkable"))
