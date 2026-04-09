from uuid import UUID

from fastapi import APIRouter, HTTPException

from src.apps.http.di import TestRunDriverDep
from src.dtos import TestCaseDTO
from src.infrastructure_ports import ObjectNotFoundError

router = APIRouter(tags=["testcases"])


@router.get("/{domain}/testcase/{testcase_id}", response_model=TestCaseDTO)
def get_testcase(
    domain: str,
    testcase_id: UUID,
    driver: TestRunDriverDep,
) -> TestCaseDTO:
    try:
        return driver.load_testcase(testcase_id=testcase_id)
    except ObjectNotFoundError as err:
        raise HTTPException(
            status_code=404, detail=f"Testcase {testcase_id} not found"
        ) from err
