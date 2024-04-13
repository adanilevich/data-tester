from src.testcase.precondition_checks.abstract_check import AbstractCheck
from src.testcase.precondition_checks.i_checkable import ICheckable


class CheckTestObjectExists(AbstractCheck):
    """
    Check if a testobject (e.g. table) exists in given domain, stage and instance.
    Uses backend from checkable (e.g. TestCase instance) to fetch database information.
    """
    name = "testobject_exists"

    def _check(self, checkable: ICheckable) -> bool:

        existing_testobjects = checkable.backend.get_testobjects(
            domain=checkable.testobject.domain,
            stage=checkable.testobject.stage,
            instance=checkable.testobject.instance,
        )

        if checkable.testobject.name in existing_testobjects:
            return True
        else:
            checkable.update_summary(f"Testobject {checkable.testobject.name} not found!")
            return False
