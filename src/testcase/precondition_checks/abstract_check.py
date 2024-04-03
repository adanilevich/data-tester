from abc import ABC, abstractmethod


from src.testcase.precondition_checks.i_checkable import ICheckable


class AbstractCheck(ABC):
    """
    Abstract checker class. Each specific check is implemented as a subclass of this
    and identified by class attribute 'name'. This also contains all common functionality,
    e.g. caching of check results.
    """

    name: str = "ABSTRACT CHECKER"  # each precondition check has own name

    @abstractmethod
    def _check(self, checkable: ICheckable) -> bool:
        """Implement actual check logic for each subclass here"""

    def check(self, checkable: ICheckable) -> bool:
        """
        Implement the actual checking logic in _check. Logic re-used accross checks is
        implemented here -- e.g. caching of check results.
        """
        return self._check(checkable=checkable)
