from abc import ABC, abstractmethod

from src.testcase.precondition_checkers.abstract_checker import AbstractChecker
from src.testcase.precondition_checkers.checkable import AbstractCheckable


class IPreconditionChecker(ABC):
    """
    Interface which defines the usage of a precondition checker. This interface is used
    by TestCase (and possibly other objects). A checker must be able to access data
    from the TestCase (e.g. a 'testobject_exists' checker will require testobject
    information as well as the backend provided by TestCase). A Precon checker shouldn't
    know all details of a TestCase -- therefore, the testcase is abstracted via the
    AbstractCheckable interface.
    """

    @abstractmethod
    def check(self, check: str, checkable: AbstractCheckable) -> bool:
        """
        Specific checkers must implement all checks required. Consumers of the interface
        (e.g. a TestCase instance) are not concerned how checks are implemented.

        Args:
            check (str): name of the check to be executed, e.g. "testobject_exists".
                These names are defined as class attributes of TestCase(s)
            checkable (AbstractCheckable): Object which conforms to AbstractCheckable
                interface. Typically a TestCase object hands over itself as checkable.

        Returns:
            bool: Check result. Must return True if all ok, otherwise False
        """
        raise NotImplementedError("Can't use AbstractChecker")


class PreConditionChecker(IPreconditionChecker):
    """
    Factory Class which fetches a specific checker (subclass of AbstractChecker)
    based on the required check ('name') and then executes the check.
    """

    def check(self, check: str, checkable: AbstractCheckable) -> bool:
        checker = self._checker_factory(check=check)
        check_result = checker.check(checkable=checkable)
        return check_result

    def _checker_factory(self, check: str) -> AbstractChecker:
        if check not in AbstractChecker.known_checks:
            raise NotImplementedError(f"Unknown checker name: {check}")

        checker = AbstractChecker.known_checks[check]()
        return checker
