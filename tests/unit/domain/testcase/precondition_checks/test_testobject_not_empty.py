import pytest

from src.domain.testcase.core.precondition_checks import (
    CheckTestObjectNotEmpty,
    ICheckable,
)
from src.dtos import TestObjectDTO


class TestTestObjectNotEmptyChecker:
    @pytest.fixture
    def checkable(self, checkable_creator) -> ICheckable:
        checkable = checkable_creator.create()

        def get_rowcount_(testobject: TestObjectDTO, *args, **kwargs) -> int:
            if "zero" in testobject.name:
                return 0
            else:
                return 10

        checkable.backend.get_rowcount = get_rowcount_

        return checkable

    def test_if_empty_nok_is_returned_and_summary_updated(self, checkable):
        checkable = checkable
        checkable.testobject.name = "zero"
        checker = CheckTestObjectNotEmpty()

        check_result = checker._check(checkable)

        assert check_result is False
        assert "Testobject zero is empty" in checkable.summary

    def test_happy_path(self, checkable):
        checkable = checkable
        checker = CheckTestObjectNotEmpty()

        check_result = checker._check(checkable)

        assert check_result is True
