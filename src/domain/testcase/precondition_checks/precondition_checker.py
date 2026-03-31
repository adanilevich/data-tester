from typing import Dict, Callable


from . import (
    IPreconditionChecker,
    ICheckable,
    AbstractCheck,
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
        self.known_checks: Dict[str, Callable] = {}
        for cls_ in AbstractCheck.__subclasses__():
            self.known_checks.update({cls_.name: cls_})

        if check not in self.known_checks:
            raise NotImplementedError(f"Unknown checker name: {check}")

        checker: AbstractCheck = self.known_checks[check]()

        return checker
