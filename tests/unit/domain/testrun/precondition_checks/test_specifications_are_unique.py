from typing import Dict

import pytest
from src.domain.testrun.precondition_checks import Checkable, CheckSpecsAreUnique
from src.dtos import (
    Importance,
    LocationDTO,
    RowcountSpecDTO,
    SchemaSpecDTO,
    SpecType,
    TestObjectDTO,
)
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


class TestCheckSpecsAreUnique:
    @pytest.fixture
    def spec(self) -> SchemaSpecDTO:
        return SchemaSpecDTO(
            location=LocationDTO(path="dummy://my_location"),
            testobject="doesnt_matter",
        )

    def test_check_fails_if_several_specs_provided(self, spec):
        checkable = DummyCheckable()
        checkable.required_specs = [SpecType.SCHEMA.value]
        checkable.specs = [spec, spec]
        checker = CheckSpecsAreUnique()

        check_result = checker._check(checkable)

        assert check_result is False
        assert "several (2) specifications were provided" in checkable.summary

    def test_check_fails_if_no_specs_are_provided(self):
        checkable = DummyCheckable()
        checkable.required_specs = [SpecType.SCHEMA.value]
        checkable.specs = []
        checker = CheckSpecsAreUnique()

        check_result = checker._check(checkable)

        assert check_result is False
        assert "No spec of type schema provided!" in checkable.summary

    def test_check_is_ok_if_unique_spec_provided(self, spec):
        checkable = DummyCheckable()
        checkable.required_specs = [
            SpecType.SCHEMA.value,
            SpecType.ROWCOUNT.value,
        ]
        new_spec = RowcountSpecDTO(
            location=spec.location,
            testobject=spec.testobject,
        )
        checkable.specs = [spec, new_spec]
        checker = CheckSpecsAreUnique()

        check_result = checker._check(checkable)

        assert check_result is True
