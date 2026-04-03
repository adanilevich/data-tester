from . import AbstractCheck, Checkable


class CheckAlwaysNok(AbstractCheck):
    """
    Dummy checker which always returns False. Test purpose only
    """

    name = "check_always_nok"

    def _check(self, checkable: Checkable) -> bool:
        return False
