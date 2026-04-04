from typing import List

from src.infrastructure_ports import IUserStorage, INotifier
from src.domain_ports import ISpec, ListSpecsCommand
from src.domain.specification.plugins import (
    INamingConventionsFactory,
    ISpecParserFactory,
)
from src.dtos import SpecDTO
from src.domain.specification.specification import Specification


class SpecAdapter(ISpec):
    """Application service for handling specification artifacts."""

    def __init__(
        self,
        naming_conventions_factory: INamingConventionsFactory,
        user_storage: IUserStorage,
        formatter_factory: ISpecParserFactory,
        notifiers: List[INotifier] | None = None,
    ):
        self.naming_conventions_factory = naming_conventions_factory
        self.user_storage = user_storage
        self.formatter_factory = formatter_factory
        self.notifiers: List[INotifier] = notifiers or []

    def list_specs(self, command: ListSpecsCommand) -> List[List[SpecDTO]]:
        """
        Find and fetch specifications for the given testcases
        and domain config.
        """
        found_specs: List[List[SpecDTO]] = []
        for testcase in command.testset.testcases.values():
            testcase_specs: List[SpecDTO] = []
            for location in command.locations:
                spec_manager = Specification(
                    user_storage=self.user_storage,
                    naming_conventions_factory=(self.naming_conventions_factory),
                    parser_factory=self.formatter_factory,
                    notifiers=self.notifiers,
                )
                testcase_specs_in_location = spec_manager.list_specs(
                    loc=location,
                    testcase=testcase,
                )
                testcase_specs.extend(testcase_specs_in_location)
            found_specs.append(testcase_specs)

        return found_specs
