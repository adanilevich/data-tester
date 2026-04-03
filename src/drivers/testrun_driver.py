from typing import List, Optional
from src.dtos import TestRunDTO
from src.domain_ports import (
    ITestRun,
    ExecuteTestRunCommand,
    SaveTestRunCommand,
    LoadTestRunCommand,
    ListTestRunsCommand,
)


class TestRunDriver:
    """Runs testcases in batch mode."""

    def __init__(self, handler: ITestRun):
        self.handler = handler

    def execute_testrun(self, testrun: TestRunDTO) -> TestRunDTO:
        """Executes a testrun and returns the result."""
        command = ExecuteTestRunCommand(testrun=testrun)
        return self.handler.execute_testrun(command=command)

    def save_testrun(self, testrun: TestRunDTO) -> None:
        """Saves a testrun."""
        command = SaveTestRunCommand(testrun=testrun)
        self.handler.save_testrun(command=command)

    def load_testrun(self, testrun_id: str) -> TestRunDTO:
        """Loads a testrun by ID."""
        command = LoadTestRunCommand(testrun_id=testrun_id)
        return self.handler.load_testrun(command=command)

    def list_testruns(
        self, domain: str, date: Optional[str] = None
    ) -> List[TestRunDTO]:
        """Lists testruns by domain and optionally by date."""
        command = ListTestRunsCommand(domain=domain, date=date)
        return self.handler.list_testruns(command=command)
