from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from src.apps.http_di import SpecDriverDep
from src.dtos import LocationDTO, TestSetDTO
from src.dtos.specification_dtos import SpecDTO

router = APIRouter(tags=["specifications"])


class FindSpecsRequest(BaseModel):
    testset: TestSetDTO
    locations: List[LocationDTO]


@router.post("/{domain}/specification/find", response_model=List[List[SpecDTO]])
def find_specifications(
    domain: str, body: FindSpecsRequest, driver: SpecDriverDep
) -> List[List[SpecDTO]]:
    return driver.find_specifications(testset=body.testset, locations=body.locations)
