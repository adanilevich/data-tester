from abc import ABC, abstractmethod
from src.dtos import TestCaseEntryDTO, LocationDTO


class INamingConventions(ABC):
    """
    Interface for naming conventions used to match specification files.
    Given a file location and the testobject and testtype, checks if the given file
    matches the naming expected for specs for the given testobject and testtype.
    """

    @abstractmethod
    def match(self, testcase: TestCaseEntryDTO, file: LocationDTO) -> bool:
        pass


class INamingConventionsFactory(ABC):
    """
    Returns naming conventions which are used for specification files of the given domain.
    """

    @abstractmethod
    def create(self, domain: str) -> INamingConventions:
        pass
