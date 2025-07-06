from typing import Dict

from src.testcase.core.precondition_checks import AbstractCheck, ICheckable


class CheckSpecsAreUnique(AbstractCheck):
    """
    Check if a testobject (e.g. table) exists in given domain, stage and instance.
    Uses backend from checkable (e.g. TestCase instance) to fetch database information.
    """
    name = "specs_are_unique"

    def _check(self, checkable: ICheckable) -> bool:

        provided_specs = checkable.specs
        provided_spec_type_counts: Dict[str, int] = {}
        for spec in provided_specs:
            if spec.type not in provided_spec_type_counts:
                provided_spec_type_counts[spec.type] = 1
            else:
                provided_spec_type_counts[spec.type] += 1

        result = True

        for required_spec_type in checkable.required_specs:
            count = provided_spec_type_counts.get(required_spec_type, 0)
            if count == 0:
                msg = f"No spec of type {required_spec_type} provided!"
                checkable.update_summary(msg)
                result = False
            elif count != 1:
                msg = (f"Specification of type {required_spec_type} must be unique,"
                       f" but several ({count}) specifications were provided.")
                checkable.update_summary(msg)
                result = False

        return result
