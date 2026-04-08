from typing import Dict

from src.domain.testrun.precondition_checks import Checkable, CheckTestObjectNotEmpty
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


class TestCheckTestObjectNotEmpty:
    def test_if_empty_nok_is_returned_and_summary_updated(self):
        checkable = DummyCheckable()
        checkable.testobject.name = "zero"

        def get_testobject_rowcount(testobject: TestObjectDTO, *args, **kwargs) -> int:
            return 0

        checkable.backend.get_testobject_rowcount = get_testobject_rowcount  # ty: ignore[invalid-assignment]
        checker = CheckTestObjectNotEmpty()

        check_result = checker._check(checkable)

        assert check_result is False
        assert "Testobject zero is empty" in checkable.summary

    def test_happy_path(self):
        checkable = DummyCheckable()

        def get_testobject_rowcount(testobject: TestObjectDTO, *args, **kwargs) -> int:
            return 10

        checkable.backend.get_testobject_rowcount = get_testobject_rowcount  # ty: ignore[invalid-assignment]
        checker = CheckTestObjectNotEmpty()

        check_result = checker._check(checkable)

        assert check_result is True
