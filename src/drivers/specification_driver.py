from src.domain_ports import FindSpecsCommand, ISpec
from src.dtos import DomainConfigDTO, TestSetDTO
from src.dtos.testrun_dtos import TestRunDefDTO


class SpecDriver:
    """Manager for finding specifications for a testset."""

    def __init__(self, spec_adapter: ISpec):
        self.adapter = spec_adapter

    def find_specs(
        self, testset: TestSetDTO, domain_config: DomainConfigDTO
    ) -> TestRunDefDTO:
        """Find specifications for all testcases in the testset.

        Locations are derived from domain_config internally.
        Returns a TestRunDefDTO with each testcase linked to its specs by name.
        """
        return self.adapter.find_specs(
            FindSpecsCommand(testset=testset, domain_config=domain_config)
        )
