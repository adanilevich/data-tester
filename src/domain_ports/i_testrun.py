from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import UUID4

from src.dtos import DTO, TestCaseDTO, TestRunDTO
from src.dtos.testrun_dtos import TestRunDefDTO


class ExecuteTestRunCommand(DTO):
    testrun_def: TestRunDefDTO
    testrun_id: UUID4 | None = None  # pre-assigned by caller (e.g. HTTP router)


class SaveTestRunCommand(DTO):
    testrun: TestRunDTO


class LoadTestRunCommand(DTO):
    testrun_id: str


class LoadTestCaseCommand(DTO):
    testcase_id: UUID4


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

    @abstractmethod
    def load_testcase(self, command: LoadTestCaseCommand) -> TestCaseDTO:
        """Load a persisted testcase by ID."""
