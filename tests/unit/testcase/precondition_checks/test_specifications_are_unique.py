import pytest

from src.testcase.precondition_checks import CheckSpecsAreUnique, ICheckable
from src.dtos import SpecificationDTO


class TestTestObjectNotEmptyChecker:

    @pytest.fixture
    def checkable(self, checkable_creator) -> ICheckable:
        checkable = checkable_creator.create()
        return checkable

    @pytest.fixture
    def spec(self) -> SpecificationDTO:
        return SpecificationDTO(location="", type="this")

    def test_check_fails_if_several_specs_provided(self, checkable, spec):
        checkable.required_specs = ["this"]
        checkable.specs = [spec, spec]
        checker = CheckSpecsAreUnique()

        check_result = checker._check(checkable)

        assert check_result is False
        assert "several (2) specifications were provided" in checkable.summary

    def test_check_fails_if_no_specs_are_provided(self, checkable):
        checkable.required_specs = ["this"]
        checkable.specs = []
        checker = CheckSpecsAreUnique()

        check_result = checker._check(checkable)

        assert check_result is False
        assert "No spec of type this provided!" in checkable.summary

    def test_check_is_ok_if_unique_spec_provided(self, checkable, spec):
        checkable.required_specs = ["this", "that"]
        new_spec = SpecificationDTO.from_dict(spec_as_dict=spec.dict())
        new_spec.type = "that"
        checkable.specs = [spec, new_spec]
        checker = CheckSpecsAreUnique()

        check_result = checker._check(checkable)

        assert check_result is True
