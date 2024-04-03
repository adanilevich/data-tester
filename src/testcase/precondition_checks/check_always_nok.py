from src.testcase.precondition_checks.abstract_check import AbstractCheck
from src.testcase.precondition_checks.i_checkable import ICheckable


class CheckAlwaysNok(AbstractCheck):
    """
    Dummy checker which always returns False. Test purpose only
    """
    name = "check_always_nok"

    def _check(self, checkable: ICheckable) -> bool:
        return False
