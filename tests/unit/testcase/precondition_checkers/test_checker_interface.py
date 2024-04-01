from typing import Dict
import pytest

from src.testcase.precondition_checkers.checkable import AbstractCheckable
from src.testcase.precondition_checkers.abstract_checker import AbstractChecker
from src.testcase.precondition_checkers.checker_interface import PreConditionChecker
from src.testcase.dtos import TestObjectDTO


class DummyCheckable(AbstractCheckable):

    def __init__(self):

        self.backend = None  # no backend will be used for testing the factory / interface
        self.testobject = TestObjectDTO(
            name="any",
            domain="any",
            project="any",
            instance="any",
        )
        self.summary = ""

    def add_detail(self, detail: Dict[str, str]):
        pass

    def update_summary(self, summary: str):
        pass

    def notify(self, message: str):
        pass


@AbstractChecker.register
class NewChecker(AbstractChecker):
    name = "check_1"

    def _check(self, checkable: AbstractCheckable) -> bool:
        return True


@AbstractChecker.register
class VeryNewChecker(AbstractChecker):
    name = "check_2"

    def _check(self, checkable: AbstractCheckable) -> bool:
        return False


def test_fetching_existing_checkers():
    checker = PreConditionChecker()

    fetched_checker = checker._checker_factory("check_1")
    assert fetched_checker.check(DummyCheckable()) is True
    assert isinstance(fetched_checker, NewChecker)

    fetched_checker = checker._checker_factory("check_2")
    assert fetched_checker.check(DummyCheckable()) is False
    assert isinstance(fetched_checker, VeryNewChecker)


def test_fetching_non_existing_checkers():
    checker = PreConditionChecker()

    with pytest.raises(NotImplementedError) as err:
        _ = checker._checker_factory("check_3")
        assert "Unknown checker name" in err


def test_that_factory_correctly_passes_results():
    checker = PreConditionChecker()
    assert checker.check("check_1", DummyCheckable()) is True
    assert checker.check("check_2", DummyCheckable()) is False
