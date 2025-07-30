from . import AbstractCheck, ICheckable
from src.dtos import DBInstanceDTO


class CheckTestObjectExists(AbstractCheck):
    """
    Check if a testobject (e.g. table) exists in given domain, stage and instance.
    Uses backend from checkable (e.g. TestCase instance) to fetch database information.
    """

    name = "testobject_exists"

    def _check(self, checkable: ICheckable) -> bool:
        db = DBInstanceDTO(
            domain=checkable.testobject.domain,
            stage=checkable.testobject.stage,
            instance=checkable.testobject.instance,
        )
        existing_testobjects = checkable.backend.get_testobjects(db)

        if checkable.testobject.name in existing_testobjects:
            return True
        else:
            checkable.update_summary(f"Testobject {checkable.testobject.name} not found!")
            return False
