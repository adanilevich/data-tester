from src.testcase.precondition_checkers.abstract_checker import AbstractChecker
from src.testcase.precondition_checkers.checkable import AbstractCheckable


@AbstractChecker.register
class TestobjectExistsChecker(AbstractChecker):
    """
    Check if a testobject (e.g. table) exists in given domain, project and instance.
    Uses backend from checkable (e.g. TestCase instance) to fetch database information.
    """
    name = "testobject_exists"

    def _check(self, checkable: AbstractCheckable) -> bool:

        existing_testobjects = checkable.backend.get_testobjects(
            domain=checkable.testobject.domain,
            project=checkable.testobject.project,
            instance=checkable.testobject.instance,
        )

        if checkable.testobject.name in existing_testobjects:
            return True
        else:
            checkable.update_summary(f"Testobject {checkable.testobject.name} not found!")
            return False
