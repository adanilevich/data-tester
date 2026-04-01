from abc import ABC, abstractmethod
from typing import Dict, Callable

from . import ICheckable


# registry of all known checks -- populated AbstractCheck.__init_cubclasses__
known_checks: Dict[str, Callable] = {}


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

    def __init_subclass__(cls, **kwargs) -> None:
        """Registers all implemented subclasses of AbstractCheck in cls.known_checks"""
        super().__init_subclass__(**kwargs)
        check_name = cls.name
        if check_name in known_checks:
            raise ValueError(f"Check {cls.__name__} already registered")
        else:
            known_checks[check_name] = cls

    def check(self, checkable: ICheckable) -> bool:
        """
        Implement the actual checking logic in _check. Logic re-used accross checks is
        implemented here -- e.g. caching of check results.
        """
        return self._check(checkable=checkable)
