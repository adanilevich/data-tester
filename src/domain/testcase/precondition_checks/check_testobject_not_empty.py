from . import AbstractCheck, ICheckable


class CheckTestObjectNotEmpty(AbstractCheck):
    """
    Check if a testobject (e.g. table) exists in given domain, stage and instance.
    Uses backend from checkable (e.g. TestCase instance) to fetch database information.
    """

    name = "testobject_not_empty"

    def _check(self, checkable: ICheckable) -> bool:
        rowcount = checkable.backend.get_rowcount(testobject=checkable.testobject)

        if rowcount > 0:
            return True
        else:
            checkable.update_summary(f"Testobject {checkable.testobject.name} is empty!")
            return False
