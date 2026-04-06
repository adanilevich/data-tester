from typing import Any, List

from fastapi import APIRouter
from pydantic import BaseModel

from src.apps.http_di import SpecDriverDep
from src.dtos import LocationDTO, TestSetDTO

router = APIRouter(tags=["specifications"])


class FindSpecsRequest(BaseModel):
    testset: TestSetDTO
    locations: List[LocationDTO]


@router.post("/{domain}/specification/find")
def find_specifications(
    domain: str, body: FindSpecsRequest, driver: SpecDriverDep
) -> Any:
    specs = driver.find_specifications(testset=body.testset, locations=body.locations)
    return [[s.to_dict(mode="json") for s in group] for group in specs]
