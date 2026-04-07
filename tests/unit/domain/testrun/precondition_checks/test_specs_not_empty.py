from typing import Dict

from src.domain.testrun.precondition_checks import Checkable, CheckSpecsNotEmpty
from src.dtos import (
    CompareSpecDTO,
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


class TestCheckSpecsNotEmpty:
    def test_empty_schema_spec_fails(self):
        checkable = DummyCheckable()
        spec = SchemaSpecDTO(
            location=LocationDTO(path="dummy://loc"),
            testobject="table1",
            columns=None,
        )
        checkable.required_specs = [SpecType.SCHEMA.value]
        checkable.specs = [spec]

        result = CheckSpecsNotEmpty()._check(checkable)

        assert result is False
        assert "schema is empty" in checkable.summary

    def test_populated_schema_spec_passes(self):
        checkable = DummyCheckable()
        spec = SchemaSpecDTO(
            location=LocationDTO(path="dummy://loc"),
            testobject="table1",
            columns={"id": "int", "name": "string"},
        )
        checkable.required_specs = [SpecType.SCHEMA.value]
        checkable.specs = [spec]

        result = CheckSpecsNotEmpty()._check(checkable)

        assert result is True

    def test_empty_rowcount_spec_fails(self):
        checkable = DummyCheckable()
        spec = RowcountSpecDTO(
            location=LocationDTO(path="dummy://loc"),
            testobject="table1",
            query=None,
        )
        checkable.required_specs = [SpecType.ROWCOUNT.value]
        checkable.specs = [spec]

        result = CheckSpecsNotEmpty()._check(checkable)

        assert result is False
        assert "rowcount is empty" in checkable.summary

    def test_populated_rowcount_spec_passes(self):
        checkable = DummyCheckable()
        spec = RowcountSpecDTO(
            location=LocationDTO(path="dummy://loc"),
            testobject="table1",
            query="SELECT COUNT(*) FROM table1",
        )
        checkable.required_specs = [SpecType.ROWCOUNT.value]
        checkable.specs = [spec]

        result = CheckSpecsNotEmpty()._check(checkable)

        assert result is True

    def test_empty_compare_spec_fails(self):
        checkable = DummyCheckable()
        spec = CompareSpecDTO(
            location=LocationDTO(path="dummy://loc"),
            testobject="table1",
            query=None,
        )
        checkable.required_specs = [SpecType.COMPARE.value]
        checkable.specs = [spec]

        result = CheckSpecsNotEmpty()._check(checkable)

        assert result is False
        assert "compare is empty" in checkable.summary

    def test_populated_compare_spec_passes(self):
        checkable = DummyCheckable()
        spec = CompareSpecDTO(
            location=LocationDTO(path="dummy://loc"),
            testobject="table1",
            query="SELECT * FROM table1",
        )
        checkable.required_specs = [SpecType.COMPARE.value]
        checkable.specs = [spec]

        result = CheckSpecsNotEmpty()._check(checkable)

        assert result is True

    def test_multiple_specs_one_empty_fails(self):
        checkable = DummyCheckable()
        schema = SchemaSpecDTO(
            location=LocationDTO(path="dummy://loc"),
            testobject="table1",
            columns={"id": "int"},
        )
        compare = CompareSpecDTO(
            location=LocationDTO(path="dummy://loc"),
            testobject="table1",
            query=None,
        )
        checkable.required_specs = [
            SpecType.SCHEMA.value,
            SpecType.COMPARE.value,
        ]
        checkable.specs = [schema, compare]

        result = CheckSpecsNotEmpty()._check(checkable)

        assert result is False
        assert "compare is empty" in checkable.summary

    def test_no_required_specs_passes(self):
        checkable = DummyCheckable()
        checkable.required_specs = None
        checkable.specs = []

        result = CheckSpecsNotEmpty()._check(checkable)

        assert result is True

    def test_no_specs_provided_passes(self):
        """Not this check's responsibility — specs_are_unique catches missing specs."""
        checkable = DummyCheckable()
        checkable.required_specs = [SpecType.SCHEMA.value]
        checkable.specs = []

        result = CheckSpecsNotEmpty()._check(checkable)

        assert result is True
