from abc import ABC, abstractmethod

from . import Checkable, known_checks


class IPreconditionChecker(ABC):
    """
    Interface which defines the usage of a precondition checker. This interface is used
    by TestCase (and possibly other objects). A checker must be able to access fixtures
    from the TestCase (e.g. a 'testobject_exists' checker will require testobject
    information as well as the backend provided by TestCase). A Precon checker shouldn't
    know all details of a TestCase -- therefore, the testcase is abstracted via the
    AbstractCheckable interface.
    """

    @abstractmethod
    def check(self, check: str, checkable: Checkable) -> bool:
        """
        Specific checkers must implement all checks which will be possibly passed
        via 'check' parameter. Consumers of this interface (e.g. a TestCase instance)
        are not concerned how checks are implemented.

        Args:
            check (str): name of the check to be executed, e.g. "testobject_exists".
                Keep in mind: a list of all required checks is defined as a class
                attribute of each subclass (test case) of TestCase
            checkable (ICheckable): Object which conforms to AbstractCheckable
                interface. Typically a TestCase object hands itself over as a checkable.

        Returns:
            bool: Check result. Returns True if check result is ok, otherwise False
        """


class PreConditionChecker(IPreconditionChecker):
    """
    Factory Class which fetches a specific checker (subclass of AbstractChecker)
    based on the required check ('name') and then executes the check.
    """

    def check(self, check: str, checkable: Checkable) -> bool:
        if check not in known_checks:
            raise NotImplementedError(f"Unknown checker name: {check}")
        else:
            checker = known_checks[check]()

        check_result: bool = checker.check(checkable=checkable)
        return check_result
