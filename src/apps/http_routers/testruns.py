from typing import List
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse

from src.apps.http_di import TestRunDriverDep
from src.client_interface.requests import ExecuteTestRunRequest
from src.dtos import TestRunDTO
from src.dtos.testrun_dtos import TestRunDefDTO

router = APIRouter(tags=["testruns"])


@router.get("/{domain}/testrun/", response_model=List[TestRunDTO])
def list_testruns(
    domain: str, driver: TestRunDriverDep, date: str | None = None
) -> List[TestRunDTO]:
    return driver.list_testruns(domain=domain, date=date)


@router.post("/{domain}/testrun/", status_code=202)
def execute_testrun(
    domain: str,
    body: ExecuteTestRunRequest,
    background_tasks: BackgroundTasks,
    testrun_driver: TestRunDriverDep,
) -> JSONResponse:
    testrun_def = TestRunDefDTO.from_testset(
        testset=body.testset,
        spec_list=body.specs,
        domain_config=body.domain_config,
    )
    # Pre-generate the ID so it can be returned in the 202 response
    # before the background task starts.
    testrun_id = uuid4()

    def _run(trd: TestRunDefDTO) -> None:
        testrun_driver.execute_testrun(testrun_def=trd, testrun_id=testrun_id)

    background_tasks.add_task(_run, testrun_def)
    return JSONResponse({"testrun_id": str(testrun_id)}, status_code=202)


@router.get("/{domain}/testrun/{testrun_id}", response_model=TestRunDTO)
def load_testrun(domain: str, testrun_id: str, driver: TestRunDriverDep) -> TestRunDTO:
    return driver.load_testrun(testrun_id=testrun_id)
