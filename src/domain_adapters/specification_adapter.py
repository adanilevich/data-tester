from typing import List

from src.domain.specification.plugins import (
    INamingConventionsFactory,
    ISpecParserFactory,
)
from src.domain.specification.specification import Specification
from src.domain_ports import FindSpecsCommand, ISpec
from src.dtos import AnySpec
from src.dtos.testrun_dtos import TestRunDefDTO
from src.infrastructure_ports import INotifier, IUserStorage


class SpecAdapter(ISpec):
    """Application service for finding specification artifacts."""

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

    def find_specs(self, command: FindSpecsCommand) -> TestRunDefDTO:
        """Find specifications for each testcase and return a TestRunDefDTO.

        Locations are derived from command.domain_config, keyed by the testset's stage.
        Each testcase is linked to its specs by name inside the returned TestRunDefDTO.
        """
        testset = command.testset
        domain_config = command.domain_config
        stage = testset.stage or testset.default_stage
        locations = domain_config.spec_locations_by_stage(stage)

        found_specs: List[List[AnySpec]] = []
        for testcase in testset.testcases.values():
            testcase_specs: List[AnySpec] = []
            for location in locations:
                spec_manager = Specification(
                    user_storage=self.user_storage,
                    naming_conventions_factory=self.naming_conventions_factory,
                    parser_factory=self.formatter_factory,
                    notifiers=self.notifiers,
                )
                testcase_specs.extend(
                    spec_manager.list_specs(loc=location, testcase=testcase)
                )
            found_specs.append(testcase_specs)

        return TestRunDefDTO.from_testset(testset, found_specs, domain_config)
