from typing import List

from src.infrastructure_ports import IStorageFactory
from src.domain_ports import (
    ISpecCommandHandler,
    FetchSpecsCommand,
    ParseSpecCommand,
)
from src.domain.specification.plugins import (
    INamingConventionsFactory,
    ISpecFormatterFactory,
)
from src.dtos import SpecificationDTO
from .specification import Specification


class SpecCommandHandler(ISpecCommandHandler):
    """Application service for handling specification artifacts."""

    def __init__(
        self,
        naming_conventions_factory: INamingConventionsFactory,
        storage_factory: IStorageFactory,
        formatter_factory: ISpecFormatterFactory,
    ):
        self.naming_conventions_factory = naming_conventions_factory
        self.storage_factory = storage_factory
        self.formatter_factory = formatter_factory
        self.spec_manager = Specification(
            storage_factory=self.storage_factory,
            naming_conventions_factory=self.naming_conventions_factory,
            formatter_factory=self.formatter_factory,
        )

    def fetch_specs(self, command: FetchSpecsCommand) -> List[List[SpecificationDTO]]:
        """
        Find and fetch specifications for the given testcases and domain config.
        """
        found_specs: List[List[SpecificationDTO]] = []
        for testcase in command.testset.testcases.values():
            testcase_specs: List[SpecificationDTO] = []
            for location in command.locations:
                # Find specifications for this testcase in the provided location
                testcase_specs_in_this_location = self.spec_manager.find_specs(
                    location=location,
                    testcase=testcase,
                    domain=command.testset.domain,
                )
                testcase_specs.extend(testcase_specs_in_this_location)
            found_specs.append(testcase_specs)

        return found_specs

    def parse_spec(self, command: ParseSpecCommand) -> List[SpecificationDTO]:
        """
        Parse specification(s) from the given file or byte object.
        """
        return self.spec_manager.parse_spec_file(
            file=command.file, testobject=command.testobject
        )
