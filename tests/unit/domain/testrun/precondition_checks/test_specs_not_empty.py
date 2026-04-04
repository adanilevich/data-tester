import pytest

from src.domain.testrun.precondition_checks import CheckSpecsNotEmpty, Checkable
from src.dtos import (
    SpecType,
    LocationDTO,
    SchemaSpecDTO,
    RowcountSpecDTO,
    CompareSpecDTO,
)


class TestCheckSpecsNotEmpty:
    @pytest.fixture
    def checkable(self, checkable_creator) -> Checkable:
        return checkable_creator.create()

    @pytest.fixture
    def checker(self) -> CheckSpecsNotEmpty:
        return CheckSpecsNotEmpty()

    def test_empty_schema_spec_fails(self, checkable, checker):
        spec = SchemaSpecDTO(
            location=LocationDTO(path="dummy://loc"),
            testobject="table1",
            columns=None,
        )
        checkable.required_specs = [SpecType.SCHEMA.value]
        checkable.specs = [spec]

        result = checker._check(checkable)

        assert result is False
        assert "schema is empty" in checkable.summary

    def test_populated_schema_spec_passes(self, checkable, checker):
        spec = SchemaSpecDTO(
            location=LocationDTO(path="dummy://loc"),
            testobject="table1",
            columns={"id": "int", "name": "string"},
        )
        checkable.required_specs = [SpecType.SCHEMA.value]
        checkable.specs = [spec]

        result = checker._check(checkable)

        assert result is True

    def test_empty_rowcount_spec_fails(self, checkable, checker):
        spec = RowcountSpecDTO(
            location=LocationDTO(path="dummy://loc"),
            testobject="table1",
            query=None,
        )
        checkable.required_specs = [SpecType.ROWCOUNT.value]
        checkable.specs = [spec]

        result = checker._check(checkable)

        assert result is False
        assert "rowcount is empty" in checkable.summary

    def test_populated_rowcount_spec_passes(self, checkable, checker):
        spec = RowcountSpecDTO(
            location=LocationDTO(path="dummy://loc"),
            testobject="table1",
            query="SELECT COUNT(*) FROM table1",
        )
        checkable.required_specs = [SpecType.ROWCOUNT.value]
        checkable.specs = [spec]

        result = checker._check(checkable)

        assert result is True

    def test_empty_compare_spec_fails(self, checkable, checker):
        spec = CompareSpecDTO(
            location=LocationDTO(path="dummy://loc"),
            testobject="table1",
            query=None,
        )
        checkable.required_specs = [SpecType.COMPARE.value]
        checkable.specs = [spec]

        result = checker._check(checkable)

        assert result is False
        assert "compare is empty" in checkable.summary

    def test_populated_compare_spec_passes(self, checkable, checker):
        spec = CompareSpecDTO(
            location=LocationDTO(path="dummy://loc"),
            testobject="table1",
            query="SELECT * FROM table1",
        )
        checkable.required_specs = [SpecType.COMPARE.value]
        checkable.specs = [spec]

        result = checker._check(checkable)

        assert result is True

    def test_multiple_specs_one_empty_fails(self, checkable, checker):
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
            SpecType.SCHEMA.value, SpecType.COMPARE.value,
        ]
        checkable.specs = [schema, compare]

        result = checker._check(checkable)

        assert result is False
        assert "compare is empty" in checkable.summary

    def test_no_required_specs_passes(self, checkable, checker):
        checkable.required_specs = None
        checkable.specs = []

        result = checker._check(checkable)

        assert result is True

    def test_no_specs_provided_passes(self, checkable, checker):
        """Not this check's responsibility — specs_are_unique catches missing specs."""
        checkable.required_specs = [SpecType.SCHEMA.value]
        checkable.specs = []

        result = checker._check(checkable)

        assert result is True
