from abc import ABC, abstractmethod
from typing import List

from src.dtos import DTO, LocationDTO, SpecDTO, TestSetDTO


class ListSpecsCommand(DTO):
    locations: List[LocationDTO]
    testset: TestSetDTO


class ISpec(ABC):
    """
    Interface for handling specification commands.
    """

    @abstractmethod
    def list_specs(self, command: ListSpecsCommand) -> List[List[SpecDTO]]:
        """
        Fetch specifications for a given testset in given locations. For each testcase
        in command.testset.testcases, corresponding specifications are searched
        and retrieved. Returns a list of specification lists, same length as
        command.testset.testcases: each entry is a list for a given testcase.
        """
