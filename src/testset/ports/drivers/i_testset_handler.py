from abc import ABC, abstractmethod
from typing import List

from src.dtos import DTO
from src.dtos.testset import TestSetDTO
from src.dtos.location import LocationDTO


class SaveTestSetCommand(DTO):
    testset: TestSetDTO
    location: LocationDTO  # where to save the testset


class LoadTestSetCommand(DTO):
    testset_id: str
    location: LocationDTO  # where to load the testset from


class ListTestSetsCommand(DTO):
    location: LocationDTO  # where to list the testsets from
    domain: str


class ITestSetCommandHandler(ABC):
    @abstractmethod
    def save_testset(self, command: SaveTestSetCommand) -> None:
        """
        Saves a TestSetDTO to the specified location.
        """

    @abstractmethod
    def load_testset(self, command: LoadTestSetCommand) -> TestSetDTO:
        """
        Loads a TestSetDTO by testset_id from the specified location.
        """

    @abstractmethod
    def list_testsets(self, command: ListTestSetsCommand) -> List[TestSetDTO]:
        """
        Lists all testsets in the specified location for the given domain.
        """
