from typing import List

from pydantic import model_validator

from src.dtos import (
    AnySpec,
    DTO,
    TestSetDTO,
    DomainConfigDTO,
    LocationDTO,
)


class FindSpecsRequest(DTO):
    testset: TestSetDTO
    locations: List[LocationDTO]


class ExecuteTestRunRequest(DTO):
    testset: TestSetDTO
    domain_config: DomainConfigDTO
    specs: List[List[AnySpec]]

    @model_validator(mode="after")
    def validate_specs_length(self) -> "ExecuteTestRunRequest":
        n_testcases = len(self.testset.testcases)
        if len(self.specs) != n_testcases:
            raise ValueError(
                f"specs length ({len(self.specs)}) must equal "
                f"number of testcases ({n_testcases})"
            )
        return self
