from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional

from src.dtos import AnySpec, Importance, TestObjectDTO
from src.infrastructure_ports import IBackend

# registry of all known checks -- populated via AbstractCheck.__init_cubclasses__
known_checks: Dict[str, Callable] = {}


class Checkable(ABC):
    """
    Defines the interface which is required by a precondition checker.
    Since precondition checkers operate on TestCase objects, TestCase inherits
    from this interface.
    """

    testobject: TestObjectDTO  # checking testobject existence required testobject spec
    backend: IBackend  # precondition checkers orchestrate backend methods
    required_specs: Optional[List[str]] = None
    specs: Optional[List[AnySpec]] = None
    summary: str = ""
    details: Optional[List[Dict[str, str | int | float]]] = None

    @abstractmethod
    def update_summary(self, summary: str):
        """Precondition checkers can update summary of the testcase/checkable."""

    @abstractmethod
    def add_detail(self, detail: Dict[str, str | int | float]):
        """Checkers can add execution details to checkable to be printed in report"""

    @abstractmethod
    def notify(self, message: str, importance: Importance = Importance.INFO):
        """Checkers are free to inform users on their actions"""


class AbstractCheck(ABC):
    """
    Abstract checker class. Each specific check is implemented as a subclass of this
    and identified by class attribute 'name'. This also contains all common functionality,
    e.g. caching of check results.
    """

    name: str = "ABSTRACT CHECKER"  # each precondition check has own name

    @abstractmethod
    def _check(self, checkable: Checkable) -> bool:
        """Implement actual check logic for each subclass here"""

    def __init_subclass__(cls, **kwargs) -> None:
        """Registers all implemented subclasses of AbstractCheck in known_checks"""
        super().__init_subclass__(**kwargs)
        check_name = cls.name
        if check_name in known_checks:
            raise ValueError(f"Check {cls.__name__} already registered")
        else:
            known_checks[check_name] = cls

    def check(self, checkable: Checkable) -> bool:
        """
        Implement the actual checking logic in _check. Logic re-used accross checks should
        be implemented here -- e.g. caching of check results.
        """
        return self._check(checkable=checkable)
