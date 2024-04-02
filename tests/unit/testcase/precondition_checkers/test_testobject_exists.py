from typing import Dict

from src.testcase.precondition_checkers.checkable import AbstractCheckable
from src.testcase.precondition_checkers.testobject_exists import TestobjectExistsChecker
from src.testcase.driven_ports.i_backend import IBackend
from src.testcase.dtos import TestObjectDTO


class DummyBackend(IBackend):

    def get_testobjects(self, *args, **kwargs):
        return ["testobject_1", "testobject_2"]


class DummyCheckable(AbstractCheckable):

    def add_detail(self, detail: Dict[str, str]):
        pass

    def update_summary(self, summary: str):
        self.summary = summary

    def notify(self, message: str):
        pass


def create_checkable(testobject: str) -> AbstractCheckable:
    checkable = DummyCheckable()
    checkable.testobject = TestObjectDTO(
        name="any", domain="any", instance="any", project="any")
    checkable.backend = DummyBackend()
    checkable.testobject.name = testobject
    return checkable


def test_checker_if_testobject_exists():
    checkable = create_checkable(testobject="testobject_1")
    checker = TestobjectExistsChecker()

    result = checker._check(checkable)

    assert result is True
    assert checkable.summary == ""


def test_checker_if_testobject_doesnt_exist():
    checkable = create_checkable(testobject="testobject_not_exists")
    checker = TestobjectExistsChecker()

    result = checker._check(checkable)

    assert result is False
    assert checkable.summary == "Testobject testobject_not_exists not found!"
