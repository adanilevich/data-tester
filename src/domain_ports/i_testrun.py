from abc import ABC, abstractmethod
from typing import List, Optional

from src.dtos import DTO, TestRunDTO


class ExecuteTestRunCommand(DTO):
    testrun: TestRunDTO


class SaveTestRunCommand(DTO):
    testrun: TestRunDTO


class LoadTestRunCommand(DTO):
    testrun_id: str


class ListTestRunsCommand(DTO):
    domain: str
    date: Optional[str] = None


class ITestRun(ABC):
    """Abstract interface to execute testcases."""

    @abstractmethod
    def execute_testrun(self, command: ExecuteTestRunCommand) -> TestRunDTO:
        """Execute testcases."""

    @abstractmethod
    def save_testrun(self, command: SaveTestRunCommand) -> None:
        """Save testrun results."""

    @abstractmethod
    def load_testrun(self, command: LoadTestRunCommand) -> TestRunDTO:
        """Load testrun results."""

    @abstractmethod
    def list_testruns(self, command: ListTestRunsCommand) -> List[TestRunDTO]:
        """List testruns by domain and optionally date."""
