from src.dtos.testset import TestSetDTO
from src.dtos.storage import LocationDTO
from src.domain_ports import (
    ITestSetCommandHandler,
    ListTestSetsCommand,
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
        testset_handler: ITestSetCommandHandler,
        storage_location: LocationDTO,
    ):
        self.storage_location = storage_location
        self.testset_handler = testset_handler

    def load_domain_testset_by_name(self, domain: str, name: str) -> TestSetDTO:
        """
        Lists all testsets for the given domain and loads the one with the requested name.
        Raises ValueError if not found.
        """
        command = ListTestSetsCommand(location=self.storage_location, domain=domain)
        testsets = self.testset_handler.list_testsets(command=command)
        for testset in testsets:
            if testset.name == name:
                return testset
        raise TestSetNotFoundError(
            f"Testset with name '{name}' not found in domain '{domain}'"
        )
