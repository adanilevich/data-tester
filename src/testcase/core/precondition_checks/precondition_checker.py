# flake8: noqa
from typing import Dict, Callable

# We need to import all subclasses of AbstractCheck  such that they are registered and can
# be created. This is done in precondition_checks.__init__.py which is imported here
from src.testcase.core.precondition_checks import (
    IPreconditionChecker, ICheckable, AbstractCheck,
    CheckAlwaysOk, CheckAlwaysNok, CheckTestObjectExists, 
    CheckTestObjectNotEmpty, CheckSpecsAreUnique, CheckPrimaryKeysAreSpecified
)


class PreConditionChecker(IPreconditionChecker):
    """
    Factory Class which fetches a specific checker (subclass of AbstractChecker)
    based on the required check ('name') and then executes the check.
    """

    known_checks: Dict[str, Callable] = dict()

    def check(self, check: str, checkable: ICheckable) -> bool:
        checker = self._checker_factory(check=check)
        check_result = checker.check(checkable=checkable)
        return check_result

    def _checker_factory(self, check: str) -> AbstractCheck:

        for cls_ in AbstractCheck.__subclasses__():
            self.known_checks.update({cls_.name: cls_})

        if check not in self.known_checks:
            raise NotImplementedError(f"Unknown checker name: {check}")

        checker = self.known_checks[check]()

        return checker
