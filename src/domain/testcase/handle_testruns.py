from typing import List, cast

from src.domain_ports import (
    ITestRunCommandHandler,
    ExecuteTestRunCommand,
    SaveTestRunCommand,
    LoadTestRunCommand,
    SetReportIdsCommand,
)
from src.infrastructure_ports import IBackendFactory, INotifier, IDtoStorage
from src.dtos import TestRunDTO, ObjectType
from .testrun import TestRun


class TestRunCommandHandler(ITestRunCommandHandler):
    """Receives a command and executes testcases"""

    # TODO: implement list_testruns method

    def __init__(
        self,
        backend_factory: IBackendFactory,
        notifiers: List[INotifier],
        dto_storage: IDtoStorage,
    ):
        self.backend_factory: IBackendFactory = backend_factory
        self.notifiers: List[INotifier] = notifiers
        self.dto_storage: IDtoStorage = dto_storage

    def execute_testrun(self, command: ExecuteTestRunCommand) -> TestRunDTO:
        testrun = TestRun(
            testrun=command.testrun,
            backend=self.backend_factory.create(
                domain_config=command.testrun.domain_config
            ),
            notifiers=self.notifiers,
            dto_storage=self.dto_storage,
        )

        result = testrun.execute()

        return result

    def save_testrun(self, command: SaveTestRunCommand) -> None:
        """Saves a testrun, e.g. to disk"""
        self.dto_storage.write_dto(dto=command.testrun)

    def load_testrun(self, command: LoadTestRunCommand) -> TestRunDTO:
        """Loads a testrun, e.g. from disk"""
        dto = self.dto_storage.read_dto(
            object_type=ObjectType.TESTRUN,
            id=command.testrun_id,
        )
        return cast(TestRunDTO, dto)

    def set_report_ids(self, command: SetReportIdsCommand) -> None:
        """Sets report ids for testrun report and testcase reports
        and persists testrun"""
        testrun = command.testrun
        testrun.report_id = command.testrun_report.report_id
        self.dto_storage.write_dto(dto=testrun)
