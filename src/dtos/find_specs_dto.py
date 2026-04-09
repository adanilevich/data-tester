from src.dtos.domain_config_dtos import DomainConfigDTO
from src.dtos.dto import DTO
from src.dtos.testset_dtos import TestSetDTO


class FindSpecsDTO(DTO):
    testset: TestSetDTO
    domain_config: DomainConfigDTO
