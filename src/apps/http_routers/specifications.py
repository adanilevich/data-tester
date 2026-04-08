from fastapi import APIRouter

from src.apps.http_di import SpecDriverDep
from src.client_interface.requests import FindSpecsRequest
from src.dtos.testrun_dtos import TestRunDefDTO

router = APIRouter(tags=["specifications"])


@router.post("/{domain}/specification/find", response_model=TestRunDefDTO)
def find_specifications(
    domain: str, body: FindSpecsRequest, driver: SpecDriverDep
) -> TestRunDefDTO:
    return driver.find_specs(testset=body.testset, domain_config=body.domain_config)
