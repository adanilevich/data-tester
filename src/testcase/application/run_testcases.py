from typing import List
from uuid import uuid4
from datetime import datetime

from src.testcase.driver_ports.i_run_testcases import (
    IRunTestCasesCommandHandler,
    RunTestCaseCommand
)
from src.testcase.driven_ports.i_backend_factory import IBackendFactory
from src.testcase.driven_ports.i_notifier import INotifier
from src.dtos.testcase import TestCaseResultDTO, TestResult, TestStatus
from src.testcase.testcases.testcase_factory import TestCaseFactory, TestCaseUnknownError


class RunTestCasesCommandHandler(IRunTestCasesCommandHandler):
    """Receives a command and executes testcases"""

    def __init__(self, backend_factory: IBackendFactory, notifiers: List[INotifier]):
        self.backend_factory: IBackendFactory = backend_factory
        self.notifiers: List[INotifier] = notifiers

    def run(self, commands: List[RunTestCaseCommand]) -> List[TestCaseResultDTO]:

        run_id = str(uuid4())
        results = []
        for command in commands:
            backend_ = self.backend_factory.create(domain_config=command.domain_config)
            try:
                testcase = TestCaseFactory.create(
                    ttype=command.testtype,
                    testobject=command.testobject,
                    specs=command.specs,
                    domain_config=command.domain_config,
                    run_id=run_id,
                    backend=backend_,
                    notifiers=self.notifiers
                )
                result = testcase.execute()
            except TestCaseUnknownError:
                result = TestCaseResultDTO(
                    id="n/a",
                    result=TestResult.NA,
                    summary=f"Test type {command.testtype} unknown!",
                    details=[],
                    status=TestStatus.ERROR,
                    start_ts=datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
                    end_ts=datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
                    testobject=command.testobject,
                    run_id=run_id,
                    diff=dict(),
                    testtype=command.testtype,
                    specifications=command.specs,
                )
            results.append(result)

        return results
