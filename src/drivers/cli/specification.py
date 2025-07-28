from typing import List
from src.domain.specification import ISpecCommandHandler, FetchSpecsCommand
from src.dtos import TestSetDTO, LocationDTO


class CliSpecManager:
    """
    CLI manager for specification handling.
    Provides methods for finding specifications from the CLI.
    """

    def __init__(self, spec_command_handler: ISpecCommandHandler):
        self.spec_command_handler = spec_command_handler

    def find_specifications(self, testset: TestSetDTO, locations: List[LocationDTO]):
        """
        Receives a TestSetDTO and returns a TestRunDTO after finding specifications.
        """
        specs = self.spec_command_handler.fetch_specs(
            FetchSpecsCommand(
                testset=testset,
                locations=locations,
            )
        )
        return specs
