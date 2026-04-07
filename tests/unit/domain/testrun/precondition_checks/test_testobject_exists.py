from typing import Dict

from src.domain.testrun.precondition_checks import CheckTestObjectExists, Checkable
from src.dtos import Importance, TestObjectDTO
from src.infrastructure.backend.dummy import DummyBackend


class DummyCheckable(Checkable):
    def __init__(self) -> None:
        self.testobject = TestObjectDTO(
            name="stage_customers", domain="payments", stage="test", instance="alpha"
        )
        self.backend = DummyBackend()
        self.summary = ""

    def update_summary(self, summary: str) -> None:
        self.summary += summary

    def add_detail(self, detail: Dict[str, str | int | float]) -> None:
        pass

    def notify(self, message: str, importance: Importance = Importance.INFO) -> None:
        pass


_TESTOBJECTS = [
    TestObjectDTO(name="testobject_1", domain="d", stage="s", instance="i"),
    TestObjectDTO(name="testobject_2", domain="d", stage="s", instance="i"),
]


def _list_testobjects(*args, **kwargs) -> list[TestObjectDTO]:
    return _TESTOBJECTS


class TestCheckTestObjectExists:
    def test_checker_if_testobject_exists(self):
        checkable = DummyCheckable()
        checkable.testobject.name = "testobject_1"
        checkable.backend.list_testobjects = _list_testobjects  # ty: ignore[invalid-assignment]
        checker = CheckTestObjectExists()

        result = checker._check(checkable)

        assert result is True
        assert checkable.summary == ""

    def test_checker_if_testobject_doesnt_exist(self):
        checkable = DummyCheckable()
        checkable.testobject.name = "testobject_not_exists"
        checkable.backend.list_testobjects = _list_testobjects  # ty: ignore[invalid-assignment]
        checker = CheckTestObjectExists()

        result = checker._check(checkable)

        assert result is False
        assert checkable.summary == "Testobject testobject_not_exists not found!"
