from typing import List

from fastapi import APIRouter, Response

from src.apps.http.di import TestSetDriverDep
from src.dtos import TestSetDTO

router = APIRouter(tags=["testsets"])


@router.get("/{domain}/testset", response_model=List[TestSetDTO])
def list_testsets(domain: str, driver: TestSetDriverDep) -> List[TestSetDTO]:
    return driver.list_testsets(domain=domain)


@router.get("/{domain}/testset/{testset_id}", response_model=TestSetDTO)
def load_testset(domain: str, testset_id: str, driver: TestSetDriverDep) -> TestSetDTO:
    return driver.load_testset(testset_id=testset_id)


@router.put("/{domain}/testset/{testset_id}", status_code=204)
def save_testset(
    domain: str, testset_id: str, dto: TestSetDTO, driver: TestSetDriverDep
) -> Response:
    driver.save_testset(testset=dto)
    return Response(status_code=204)
