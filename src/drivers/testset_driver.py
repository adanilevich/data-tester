from typing import List
from src.dtos.testset_dtos import TestSetDTO
from src.domain_ports import (
    ITestSet,
    ListTestSetsCommand,
    LoadTestSetCommand,
)


class TestSetDriverError(Exception):
    """
    Exception raised when a testset manager operation fails.
    """


class TestSetNotFoundError(TestSetDriverError):
    """
    Exception raised when a testset is not found.
    """


class TestSetDriver:
    """
    Testset manager for non-interactive execution. Loads a testset for a given
    domain and testset name (which is passed as argument or from environment).
    """

    def __init__(
        self,
        testset_adapter: ITestSet,
    ):
        self.adapter = testset_adapter

    def load_testset(self, testset_id: str) -> TestSetDTO:
        """Loads a testset by ID."""
        command = LoadTestSetCommand(testset_id=testset_id)
        return self.adapter.load_testset(command=command)

    def list_testsets(self, domain: str) -> List[TestSetDTO]:
        """Lists all testsets for the given domain."""
        command = ListTestSetsCommand(domain=domain)
        return self.adapter.list_testsets(command=command)

    def load_domain_testset_by_name(
        self, domain: str, name: str
    ) -> TestSetDTO:
        """
        Lists all testsets for the given domain and loads
        the one with the requested name.
        Raises ValueError if not found.
        """
        command = ListTestSetsCommand(domain=domain)
        testsets = self.adapter.list_testsets(
            command=command
        )
        for testset in testsets:
            if testset.name == name:
                return testset
        raise TestSetNotFoundError(
            f"Testset with name '{name}' not found "
            f"in domain '{domain}'"
        )
