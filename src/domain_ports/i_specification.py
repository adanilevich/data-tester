from abc import ABC, abstractmethod

from src.dtos import DTO, DomainConfigDTO, TestSetDTO
from src.dtos.testrun_dtos import TestRunDefDTO


class FindSpecsCommand(DTO):
    testset: TestSetDTO
    domain_config: DomainConfigDTO


class ISpec(ABC):
    """Interface for finding specifications for a given testset."""

    @abstractmethod
    def find_specs(self, command: FindSpecsCommand) -> TestRunDefDTO:
        """Find specifications for each testcase in command.testset, using locations
        derived from command.domain_config. Returns a TestRunDefDTO linking each
        testcase to its found specs by name."""
