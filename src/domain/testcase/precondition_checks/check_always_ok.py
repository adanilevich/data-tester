from . import AbstractCheck, Checkable


class CheckAlwaysOk(AbstractCheck):
    """
    Dummy checker which always returns True. Test purpose only
    """

    name = "check_always_ok"

    def _check(self, checkable: Checkable) -> bool:
        return True
