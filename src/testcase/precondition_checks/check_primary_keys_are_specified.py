from typing import List

from src.testcase.precondition_checks import AbstractCheck, ICheckable
from src.dtos import SchemaSpecificationDTO


class CheckPrimaryKeysAreSpecified(AbstractCheck):
    """
    Check if a testobject (e.g. table) exists in given domain, stage and instance.
    Uses backend from checkable (e.g. TestCase instance) to fetch database information.
    """
    name = "primary_keys_are_specified"

    def _check(self, checkable: ICheckable) -> bool:

        primary_keys: List[str] = []
        for spec in checkable.specs:
            if isinstance(spec, SchemaSpecificationDTO) and spec.primary_keys is not None:
                primary_keys = spec.primary_keys

        if len(primary_keys) == 0:
            checkable.update_summary("Primary keys not specified")
            result = False
        else:
            result = True

        return result
