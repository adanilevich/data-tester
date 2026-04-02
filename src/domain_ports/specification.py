from abc import ABC, abstractmethod
from typing import List

from src.dtos import LocationDTO, DTO, SpecificationDTO, TestSetDTO


class FetchSpecsCommand(DTO):
    locations: List[LocationDTO]
    testset: TestSetDTO


class ParseSpecCommand(DTO):
    file: bytes
    testobject: str


class ISpecCommandHandler(ABC):
    """
    Interface for handling specification commands.
    """

    @abstractmethod
    def fetch_specs(self, command: FetchSpecsCommand) -> List[List[SpecificationDTO]]:
        """
        Fetch specifications for a given testset in given locations. For each testcase
        in command.testset.testcases, corresponding specifications are searched
        and retrieved. Returns a list of specification lists, same length as
        command.testset.testcases: each entry is a list for a given testcase.
        """

    @abstractmethod
    def parse_spec(self, command: ParseSpecCommand) -> List[SpecificationDTO]:
        pass
