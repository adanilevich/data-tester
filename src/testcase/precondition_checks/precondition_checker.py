from typing import Dict

from src.testcase.precondition_checks import (
    IPreconditionChecker,
    ICheckable,
    AbstractCheck,
    CheckTestObjectExists,
    CheckTestObjectNotEmpty,
    CheckAlwaysOk,
    CheckAlwaysNok
)


class PreConditionChecker(IPreconditionChecker):
    """
    Factory Class which fetches a specific checker (subclass of AbstractChecker)
    based on the required check ('name') and then executes the check.
    """

    # TODO: rework this to be similar to testcase factory
    known_checks: Dict = {
        "testobject_exists": CheckTestObjectExists,
        "testobject_not_empty": CheckTestObjectNotEmpty,
        "check_always_ok": CheckAlwaysOk,
        "check_always_nok": CheckAlwaysNok,
    }

    def check(self, check: str, checkable: ICheckable) -> bool:
        checker = self._checker_factory(check=check)
        check_result = checker.check(checkable=checkable)
        return check_result

    def _checker_factory(self, check: str) -> AbstractCheck:
        if check not in self.known_checks:
            raise NotImplementedError(f"Unknown checker name: {check}")

        checker = self.known_checks[check]()
        return checker
