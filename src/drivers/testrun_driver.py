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

    def __init__(self, testrun_adapter: ITestRun):
        self.adapter = testrun_adapter

    def execute_testrun(self, testrun: TestRunDTO) -> TestRunDTO:
        """Executes a testrun and returns the result."""
        command = ExecuteTestRunCommand(testrun=testrun)
        return self.adapter.execute_testrun(command=command)

    def save_testrun(self, testrun: TestRunDTO) -> None:
        """Saves a testrun."""
        command = SaveTestRunCommand(testrun=testrun)
        self.adapter.save_testrun(command=command)

    def load_testrun(self, testrun_id: str) -> TestRunDTO:
        """Loads a testrun by ID."""
        command = LoadTestRunCommand(testrun_id=testrun_id)
        return self.adapter.load_testrun(command=command)

    def list_testruns(
        self, domain: str, date: Optional[str] = None
    ) -> List[TestRunDTO]:
        """Lists testruns by domain and optionally by date."""
        command = ListTestRunsCommand(domain=domain, date=date)
        return self.adapter.list_testruns(command=command)
