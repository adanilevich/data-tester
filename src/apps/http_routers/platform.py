from typing import List

from fastapi import APIRouter

from src.apps.http_di import DomainConfigDriverDep, PlatformDriverDep
from src.dtos import DBInstanceDTO, TestObjectDTO

router = APIRouter(tags=["platform"])


@router.get("/{domain}/platform/testobjects", response_model=List[TestObjectDTO])
def list_testobjects(
    domain: str,
    stage: str,
    instance: str,
    platform_driver: PlatformDriverDep,
    domain_config_driver: DomainConfigDriverDep,
) -> List[TestObjectDTO]:
    domain_config = domain_config_driver.load_domain_config(domain=domain)
    db = DBInstanceDTO(domain=domain, stage=stage, instance=instance)
    return platform_driver.list_testobjects(domain_config=domain_config, db=db)
