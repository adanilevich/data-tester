from typing import List

from src.infrastructure_ports import IUserStorage
from src.domain_ports import (
    ISpec,
    ListSpecsCommand,
    ParseSpecCommand,
)
from src.domain.specification.plugins import (
    INamingConventionsFactory,
    ISpecFormatterFactory,
)
from src.dtos import SpecificationDTO
from src.domain.specification.specification import Specification


class SpecAdapter(ISpec):
    """Application service for handling specification artifacts."""

    def __init__(
        self,
        naming_conventions_factory: INamingConventionsFactory,
        user_storage: IUserStorage,
        formatter_factory: ISpecFormatterFactory,
    ):
        self.naming_conventions_factory = naming_conventions_factory
        self.user_storage = user_storage
        self.formatter_factory = formatter_factory

    def list_specs(
        self, command: ListSpecsCommand
    ) -> List[List[SpecificationDTO]]:
        """
        Find and fetch specifications for the given testcases
        and domain config.
        """
        found_specs: List[List[SpecificationDTO]] = []
        for testcase in command.testset.testcases.values():
            testcase_specs: List[SpecificationDTO] = []
            for location in command.locations:
                spec_manager = Specification(
                    user_storage=self.user_storage,
                    naming_conventions_factory=(
                        self.naming_conventions_factory
                    ),
                    formatter_factory=self.formatter_factory,
                )
                testcase_specs_in_location = (
                    spec_manager.find_specs(
                        location=location,
                        testcase=testcase,
                        domain=command.testset.domain,
                    )
                )
                testcase_specs.extend(testcase_specs_in_location)
            found_specs.append(testcase_specs)

        return found_specs

    def parse_spec(
        self, command: ParseSpecCommand
    ) -> List[SpecificationDTO]:
        """
        Parse specification(s) from the given file or byte object.
        """
        spec_manager = Specification(
            user_storage=self.user_storage,
            naming_conventions_factory=(
                self.naming_conventions_factory
            ),
            formatter_factory=self.formatter_factory,
        )
        return spec_manager.parse_spec_file(
            file=command.file, testobject=command.testobject
        )
