import pytest

from src.testcase.core.precondition_checks import CheckSpecsAreUnique, ICheckable
from src.dtos import SpecificationDTO, SpecificationType, LocationDTO


class TestTestObjectNotEmptyChecker:

    @pytest.fixture
    def checkable(self, checkable_creator) -> ICheckable:
        checkable = checkable_creator.create()
        return checkable

    @pytest.fixture
    def spec(self) -> SpecificationDTO:
        return SpecificationDTO(
            location=LocationDTO(path="dummy://my_location"),
            spec_type=SpecificationType.SCHEMA,
            testobject="doesnt_matter",
        )

    def test_check_fails_if_several_specs_provided(self, checkable, spec):
        checkable.required_specs = [SpecificationType.SCHEMA.value]
        checkable.specs = [spec, spec]
        checker = CheckSpecsAreUnique()

        check_result = checker._check(checkable)

        assert check_result is False
        assert "several (2) specifications were provided" in checkable.summary

    def test_check_fails_if_no_specs_are_provided(self, checkable):
        checkable.required_specs = [SpecificationType.SCHEMA.value]
        checkable.specs = []
        checker = CheckSpecsAreUnique()

        check_result = checker._check(checkable)

        assert check_result is False
        assert "No spec of type schema provided!" in checkable.summary

    def test_check_is_ok_if_unique_spec_provided(self, checkable, spec):
        checkable.required_specs = [
            SpecificationType.SCHEMA.value, SpecificationType.ROWCOUNT_SQL.value]
        new_spec = SpecificationDTO.from_dict(spec.to_dict())
        new_spec.spec_type = SpecificationType.ROWCOUNT_SQL
        checkable.specs = [spec, new_spec]
        checker = CheckSpecsAreUnique()

        check_result = checker._check(checkable)

        assert check_result is True
