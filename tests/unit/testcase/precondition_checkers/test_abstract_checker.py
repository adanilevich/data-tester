from src.testcase.precondition_checkers.checkable import AbstractCheckable
from src.testcase.precondition_checkers.abstract_checker import AbstractChecker


@AbstractChecker.register
class NewChecker(AbstractChecker):
    name = "name"

    def _check(self, checkable: AbstractCheckable) -> bool:
        return True


def test_registering_of_new_checkers():

    print(AbstractChecker.known_checks)
    assert "name" in AbstractChecker.known_checks
    assert AbstractChecker.known_checks["name"] == NewChecker
