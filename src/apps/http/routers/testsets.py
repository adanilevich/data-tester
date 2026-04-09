from typing import List

from fastapi import APIRouter, HTTPException, Response

from src.apps.http.di import TestSetDriverDep
from src.dtos import TestSetDTO
from src.infrastructure_ports import ObjectNotFoundError

router = APIRouter(tags=["testsets"])


@router.get("/{domain}/testset", response_model=List[TestSetDTO])
def list_testsets(domain: str, driver: TestSetDriverDep) -> List[TestSetDTO]:
    return driver.list_testsets(domain=domain)


@router.get("/{domain}/testset/{testset_id}", response_model=TestSetDTO)
def load_testset(domain: str, testset_id: str, driver: TestSetDriverDep) -> TestSetDTO:
    try:
        return driver.load_testset(testset_id=testset_id)
    except ObjectNotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err


@router.put("/{domain}/testset/{testset_id}", status_code=204)
def save_testset(
    domain: str, testset_id: str, dto: TestSetDTO, driver: TestSetDriverDep
) -> Response:
    if str(dto.testset_id) != testset_id:
        raise HTTPException(status_code=422, detail="testset_id in URL must match body")
    driver.save_testset(testset=dto)
    return Response(status_code=204)


@router.delete("/{domain}/testset/{testset_id}", status_code=204)
def delete_testset(domain: str, testset_id: str, driver: TestSetDriverDep) -> Response:
    try:
        driver.delete_testset(testset_id=testset_id)
    except ObjectNotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err
    return Response(status_code=204)
