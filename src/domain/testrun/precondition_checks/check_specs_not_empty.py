from typing import List

from src.dtos.specification_dtos import AnySpec

from . import AbstractCheck, Checkable


class CheckSpecsNotEmpty(AbstractCheck):
    """
    Check that all required specifications contain data (are not empty).
    A spec is considered empty when its core field is None, e.g. columns for schema
    specs, query for rowcount/compare specs.
    """

    name = "specs_not_empty"

    def _check(self, checkable: Checkable) -> bool:
        provided_specs: List[AnySpec] = checkable.specs or []
        result = True

        for required_spec_type in checkable.required_specs or []:
            for spec in provided_specs:
                if spec.spec_type.value == required_spec_type and spec.empty:
                    msg = f"Specification of type {required_spec_type} is empty!"
                    checkable.update_summary(msg)
                    checkable.notify(msg)
                    result = False

        return result
