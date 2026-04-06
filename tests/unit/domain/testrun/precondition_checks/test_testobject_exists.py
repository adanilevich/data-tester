from typing import List
import pytest

from src.dtos import TestObjectDTO
from src.domain.testrun.precondition_checks import Checkable, CheckTestObjectExists


class TestTestObjectExistsChecker:
    @pytest.fixture
    def checkable(self, checkable_creator) -> Checkable:
        checkable = checkable_creator.create()

        def list_testobjects_(*args, **kwargs) -> List[TestObjectDTO]:
            return [
                TestObjectDTO(name="testobject_1", domain="d", stage="s", instance="i"),
                TestObjectDTO(name="testobject_2", domain="d", stage="s", instance="i"),
            ]

        checkable.backend.list_testobjects = list_testobjects_

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
