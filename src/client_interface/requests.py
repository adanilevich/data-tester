from typing import Any, List

from pydantic import BaseModel, model_validator

from src.dtos import (
    SpecDTO,
    SpecFactory,
    TestSetDTO,
    DomainConfigDTO,
    LocationDTO
)

_spec_factory = SpecFactory()


class FindSpecsRequest(BaseModel):
    testset: TestSetDTO
    locations: List[LocationDTO]


class ExecuteTestRunRequest(BaseModel):
    testset: TestSetDTO
    domain_config: DomainConfigDTO
    spec_list: List[List[SpecDTO]]

    # TODO: why do we need this?
    @model_validator(mode="before")
    @classmethod
    def deserialize_specs(cls, data: Any) -> Any:
        """Deserialize specs into proper subclasses (e.g. SchemaSpecDTO)."""
        if isinstance(data, dict) and "spec_list" in data:
            raw = data["spec_list"]
            data["spec_list"] = [
                [_spec_factory.create_from_dict(s) for s in group] for group in raw
            ]
        return data

    @model_validator(mode="after")
    def validate_spec_list_length(self) -> "ExecuteTestRunRequest":
        n_testcases = len(self.testset.testcases)
        if len(self.spec_list) != n_testcases:
            raise ValueError(
                f"spec_list length ({len(self.spec_list)}) must equal "
                f"number of testcases ({n_testcases})"
            )
        return self
