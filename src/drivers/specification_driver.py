from typing import List
from src.domain_ports import ISpec, ListSpecsCommand
from src.dtos import TestSetDTO, LocationDTO


class SpecDriver:
    """
    Manager for specification handling.
    Provides methods for finding specifications.
    """

    def __init__(self, spec_command_handler: ISpec):
        self.spec_command_handler = spec_command_handler

    def find_specifications(self, testset: TestSetDTO, locations: List[LocationDTO]):
        """
        Receives a TestSetDTO and returns a TestRunDTO after finding specifications.
        """
        specs = self.spec_command_handler.list_specs(
            ListSpecsCommand(
                testset=testset,
                locations=locations,
            )
        )
        return specs
