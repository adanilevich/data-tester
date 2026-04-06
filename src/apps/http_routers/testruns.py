from typing import List

from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, model_validator

from src.apps.http_di import ReportDriverDep, TestRunDriverDep
from src.dtos import DomainConfigDTO, TestRunDTO, TestSetDTO
from src.dtos.specification_dtos import SpecDTO
from src.dtos.testrun_dtos import TestStatus

router = APIRouter(tags=["testruns"])


class ExecuteTestRunRequest(BaseModel):
    testset: TestSetDTO
    domain_config: DomainConfigDTO
    spec_list: List[List[SpecDTO]]

    @model_validator(mode="after")
    def validate_spec_list_length(self) -> "ExecuteTestRunRequest":
        n_testcases = len(self.testset.testcases)
        if len(self.spec_list) != n_testcases:
            raise ValueError(
                f"spec_list length ({len(self.spec_list)}) must equal "
                f"number of testcases ({n_testcases})"
            )
        return self


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
    report_driver: ReportDriverDep,
) -> JSONResponse:
    testrun = TestRunDTO.from_testset(
        testset=body.testset,
        spec_list=body.spec_list,
        domain_config=body.domain_config,
    )
    testrun.status = TestStatus.INITIATED
    testrun_driver.save_testrun(testrun=testrun)

    def _run(tr: TestRunDTO) -> None:
        result = testrun_driver.execute_testrun(testrun=tr)
        report_driver.create_and_save_all_reports(testrun=result)

    background_tasks.add_task(_run, testrun)
    return JSONResponse({"testrun_id": str(testrun.testrun_id)}, status_code=202)


@router.get("/{domain}/testrun/{testrun_id}", response_model=TestRunDTO)
def load_testrun(domain: str, testrun_id: str, driver: TestRunDriverDep) -> TestRunDTO:
    return driver.load_testrun(testrun_id=testrun_id)
