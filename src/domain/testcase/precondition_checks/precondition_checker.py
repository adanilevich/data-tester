from . import (
    IPreconditionChecker,
    ICheckable,
    AbstractCheck,
    known_checks
)


class PreConditionChecker(IPreconditionChecker):
    """
    Factory Class which fetches a specific checker (subclass of AbstractChecker)
    based on the required check ('name') and then executes the check.
    """

    def check(self, check: str, checkable: ICheckable) -> bool:
        checker: AbstractCheck = self._checker_factory(check=check)
        check_result: bool = checker.check(checkable=checkable)
        return check_result

    def _checker_factory(self, check: str) -> AbstractCheck:

        if check not in known_checks:
            raise NotImplementedError(f"Unknown checker name: {check}")

        checker: AbstractCheck = known_checks[check]()

        return checker
