from typing import Dict, List
import pytest

from src.testcase.precondition_checks import ICheckable, CheckTestObjectExists


class TestTestObjectExistsChecker:

    @pytest.fixture
    def checkable(self, checkable_creator) -> ICheckable:
        checkable = checkable_creator.create()

        def get_testobjects_(*args, **kwargs) -> List[str]:
            return ["testobject_1", "testobject_2"]

        checkable.backend.get_testobjects = get_testobjects_

        return checkable

    def test_checker_if_testobject_exists(self, checkable):
        checkable = checkable
        checkable.testobject.name = "testobject_1"
        checker = CheckTestObjectExists()

        result = checker._check(checkable)

        assert result is True
        assert checkable.summary == ""

    def test_checker_if_testobject_doesnt_exist(self, checkable):
        checkable = checkable
        checkable.testobject.name = "testobject_not_exists"
        checker = CheckTestObjectExists()

        result = checker._check(checkable)

        assert result is False
        assert checkable.summary == "Testobject testobject_not_exists not found!"
