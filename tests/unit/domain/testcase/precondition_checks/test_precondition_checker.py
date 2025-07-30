from typing import Dict
import pytest

from src.domain.testcase.precondition_checks import (
    ICheckable,
    PreConditionChecker,
    CheckTestObjectExists,
    CheckAlwaysOk,
    CheckAlwaysNok,
)
from src.dtos import TestObjectDTO


class DummyCheckable(ICheckable):
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

    def notify(self, message: str):
        pass


def test_fetching_existing_checkers():
    factory = PreConditionChecker()

    expected = {
        "testobject_exists": CheckTestObjectExists,
        "check_always_ok": CheckAlwaysOk,
        "check_always_nok": CheckAlwaysNok,
    }

    for check, expected_checker in expected.items():
        fetched_checker = factory._checker_factory(check)
        assert isinstance(fetched_checker, expected_checker)


def test_fetching_non_existing_checkers():
    factory = PreConditionChecker()

    with pytest.raises(NotImplementedError) as err:
        _ = factory._checker_factory("check_3")

    assert "Unknown checker name" in str(err)


def test_that_factory_correctly_passes_results():
    factory = PreConditionChecker()
    assert factory.check("check_always_ok", DummyCheckable()) is True
    assert factory.check("check_always_nok", DummyCheckable()) is False
