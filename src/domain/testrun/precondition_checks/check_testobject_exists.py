from . import AbstractCheck, Checkable
from src.dtos import DBInstanceDTO


class CheckTestObjectExists(AbstractCheck):
    """
    Check if a testobject (e.g. table) exists in given domain, stage and instance.
    Uses backend from checkable (e.g. TestCase instance) to fetch database information.
    """

    name = "testobject_exists"

    def _check(self, checkable: Checkable) -> bool:
        db = DBInstanceDTO.from_testobject(checkable.testobject)
        existing = checkable.backend.list_testobjects(db)
        existing_names = [t.name for t in existing]

        if checkable.testobject.name in existing_names:
            return True
        else:
            checkable.update_summary(f"Testobject {checkable.testobject.name} not found!")
            return False
