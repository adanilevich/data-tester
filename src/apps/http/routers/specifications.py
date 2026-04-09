from fastapi import APIRouter

from src.apps.http.di import SpecDriverDep
from src.dtos import FindSpecsDTO
from src.dtos.testrun_dtos import TestRunDefDTO

router = APIRouter(tags=["specifications"])


@router.post("/{domain}/specification/find", response_model=TestRunDefDTO)
def find_specifications(
    domain: str, body: FindSpecsDTO, driver: SpecDriverDep
) -> TestRunDefDTO:
    return driver.find_specs(testset=body.testset, domain_config=body.domain_config)
