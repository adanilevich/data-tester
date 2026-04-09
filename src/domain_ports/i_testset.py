from abc import ABC, abstractmethod
from typing import List

from src.dtos import DTO
from src.dtos.testset_dtos import TestSetDTO


class SaveTestSetCommand(DTO):
    testset: TestSetDTO


class LoadTestSetCommand(DTO):
    testset_id: str


class ListTestSetsCommand(DTO):
    domain: str


class DeleteTestSetCommand(DTO):
    testset_id: str


class ITestSet(ABC):
    @abstractmethod
    def save_testset(self, command: SaveTestSetCommand) -> None:
        """
        Saves a TestSetDTO.
        """

    @abstractmethod
    def load_testset(self, command: LoadTestSetCommand) -> TestSetDTO:
        """
        Loads a TestSetDTO by testset_id.
        """

    @abstractmethod
    def delete_testset(self, command: DeleteTestSetCommand) -> None:
        """Deletes a testset by ID."""

    @abstractmethod
    def list_testsets(self, command: ListTestSetsCommand) -> List[TestSetDTO]:
        """
        Lists all testsets for the given domain.
        """
