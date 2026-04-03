from typing import List
from src.domain_ports import ISpec, ListSpecsCommand
from src.dtos import TestSetDTO, LocationDTO


class SpecDriver:
    """
    Manager for specification handling.
    Provides methods for finding specifications.
    """

    def __init__(self, spec_adapter: ISpec):
        self.adapter = spec_adapter

    def find_specifications(self, testset: TestSetDTO, locations: List[LocationDTO]):
        """
        Receives a TestSetDTO and returns a TestRunDTO after finding specifications.
        """
        specs = self.adapter.list_specs(
            ListSpecsCommand(
                testset=testset,
                locations=locations,
            )
        )
        return specs
