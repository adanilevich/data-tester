from src.testcase.precondition_checks.abstract_check import AbstractCheck
from src.testcase.precondition_checks.i_checkable import ICheckable


class CheckAlwaysOk(AbstractCheck):
    """
    Dummy checker which always returns True. Test purpose only
    """
    name = "check_always_ok"

    def _check(self, checkable: ICheckable) -> bool:
        return True
