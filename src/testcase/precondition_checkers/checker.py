from abc import ABC, abstractmethod
from src.testcase.precondition_checkers.checkable import AbstractCheckable


class AbstractChecker(ABC):

    @abstractmethod
    def check(self, check: str, checkable: AbstractCheckable) -> bool:
        raise NotImplementedError("Can't use AbstractChecker")


class PreConditionChecker(AbstractChecker):

    def check(self, check: str, checkable: AbstractCheckable) -> bool:
        return True
