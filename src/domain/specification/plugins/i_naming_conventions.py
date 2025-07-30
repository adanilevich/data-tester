from abc import ABC, abstractmethod
from typing import Tuple, List

from src.dtos import TestCaseEntryDTO, LocationDTO, SpecificationType


class INamingConventions(ABC):
    """
    Interface for naming conventions used to match specification files.
    Given a file location and the testobject and testtype, checks if the given file
    matches the naming expected for specs for the given testobject and testtype.
    """

    @abstractmethod
    def match(
        self, testcase: TestCaseEntryDTO, file: LocationDTO
    ) -> Tuple[bool, List[SpecificationType]]:
        """
        Check if a filename matches the naming convention for the given testobject
        and testtype. Returns a tuple of a boolean indicating if the filename matches
        the naming convention and the specification types of the file. If the filename
        does not match the naming convention, the specification types is empty.
        """
        pass


class INamingConventionsFactory(ABC):
    """
    Returns naming conventions which are used for specification files of the given domain.
    """

    @abstractmethod
    def create(self, domain: str) -> INamingConventions:
        pass
