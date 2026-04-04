from typing import Dict
import pytest

from src.domain.testrun.precondition_checks import Checkable, PreConditionChecker
from src.dtos import TestObjectDTO, Importance


class DummyCheckable(Checkable):
    def __init__(self):
        self.testobject = TestObjectDTO(
            name="any",
            domain="any",
            stage="any",
            instance="any",
        )
        self.summary = ""

    def add_detail(self, detail: Dict[str, str | int | float]):
        pass

    def update_summary(self, summary: str):
        pass

    def notify(self, message: str, importance: Importance = Importance.INFO):
        pass


def test_using_existing_checks():
    checker = PreConditionChecker()
    checkable = DummyCheckable()

    result = checker.check(check="check_always_ok", checkable=checkable)
    assert result is True
    result = checker.check(check="check_always_nok", checkable=checkable)
    assert result is False


def test_using_non_existing_checks():
    checker = PreConditionChecker()
    checkable = DummyCheckable()

    with pytest.raises(NotImplementedError) as err:
        _ = checker.check(check="check_3", checkable=checkable)

    assert "Unknown checker name" in str(err)
