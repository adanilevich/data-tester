from src.testcase.precondition_checks import AbstractCheck, ICheckable


class CheckAlwaysOk(AbstractCheck):
    """
    Dummy checker which always returns True. Test purpose only
    """
    name = "check_always_ok"

    def _check(self, checkable: ICheckable) -> bool:
        return True
