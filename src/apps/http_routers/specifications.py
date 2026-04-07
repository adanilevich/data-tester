from typing import Any

from fastapi import APIRouter

from src.apps.http_di import SpecDriverDep
from src.client_interface.requests import FindSpecsRequest

router = APIRouter(tags=["specifications"])


## TODO: change response to list of list of specs
@router.post("/{domain}/specification/find")
def find_specifications(
    domain: str, body: FindSpecsRequest, driver: SpecDriverDep
) -> Any:
    specs = driver.find_specifications(testset=body.testset, locations=body.locations)
    return [[s.to_dict(mode="json") for s in group] for group in specs]
