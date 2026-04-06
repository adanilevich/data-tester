from typing import Dict

from fastapi import APIRouter, Response

from src.apps.http_di import DomainConfigDriverDep
from src.dtos import DomainConfigDTO

router = APIRouter(tags=["domain-config"])


@router.get("/domain-config", response_model=Dict[str, DomainConfigDTO])
def list_domain_configs(driver: DomainConfigDriverDep) -> Dict[str, DomainConfigDTO]:
    return driver.list_domain_configs()


@router.get("/domain-config/{domain}", response_model=DomainConfigDTO)
@router.get("/{domain}/domain-config", response_model=DomainConfigDTO)
def load_domain_config(domain: str, driver: DomainConfigDriverDep) -> DomainConfigDTO:
    return driver.load_domain_config(domain=domain)


@router.put("/domain-config/{domain}", status_code=204)
def save_domain_config(
    domain: str, dto: DomainConfigDTO, driver: DomainConfigDriverDep
) -> Response:
    driver.save_domain_config(config=dto)
    return Response(status_code=204)
