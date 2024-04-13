from src.testcase.precondition_checks import AbstractCheck, ICheckable


class CheckAlwaysNok(AbstractCheck):
    """
    Dummy checker which always returns False. Test purpose only
    """
    name = "check_always_nok"

    def _check(self, checkable: ICheckable) -> bool:
        return False
