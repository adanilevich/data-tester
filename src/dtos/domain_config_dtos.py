from typing import Dict, List

from pydantic import Field

from src.dtos.dto import DTO
from src.dtos.storage_dtos import LocationDTO


class DomainConfigDTO(DTO):
    """Configuration for a single domain's test execution."""

    domain: str
    # stage → list of instance names (e.g. {"test": ["alpha", "beta"], "uat": ["main"]})
    instances: Dict[str, List[str]]
    # data types included in schema column-type comparison
    compare_datatypes: List[str]
    # default number of rows sampled for compare test cases
    sample_size_default: int
    # per-object overrides for sample size, keyed by testobject name
    sample_size_per_object: Dict[str, int] = Field(default_factory=dict)
    # stage → list of spec location path strings (e.g. {"test": ["local:///path/"]})
    spec_locations: Dict[str, List[str]]
    # storage location where test reports are written
    reports_location: LocationDTO

    @property
    def id(self) -> str:
        """Object ID for storage purposes."""
        return self.domain

    def spec_locations_by_stage(self, stage: str) -> List[LocationDTO]:
        """Return spec LocationDTOs for the given stage.

        Raises KeyError if the stage has no configured spec locations.
        """
        paths = self.spec_locations.get(stage)
        if paths is None:
            raise KeyError(f"No spec locations defined for stage '{stage}'")
        return [LocationDTO(p) for p in paths]
