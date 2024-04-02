from abc import ABC, abstractmethod
from typing import Dict

from src.testcase.precondition_checkers.checkable import AbstractCheckable


class AbstractChecker(ABC):
    """
    Abstract checker class. Each specific check is implemented as a subclass of this
    and identified by class attribute 'name'. This also contains all common functionality,
    e.g. caching of check results.
    """

    name: str = "ABSTRACT CHECKER"  # each precondition check has own name
    known_checks: Dict = dict()

    @classmethod
    def register(cls, checker_class):
        """Decorator to register new checker subclasses based on name."""
        cls.known_checks.update({checker_class.name: checker_class})
        return checker_class

    @abstractmethod
    def _check(self, checkable: AbstractCheckable) -> bool:
        """Implement actual check logic for each subclass here"""

    def check(self, checkable: AbstractCheckable) -> bool:
        """
        Implement the actual checking logic in _check. Logic re-used accross checks is
        implemented here -- e.g. caching of check results.
        """
        return self._check(checkable=checkable)
