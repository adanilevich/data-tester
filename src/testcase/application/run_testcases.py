from typing import List
from uuid import uuid4
from datetime import datetime

from src.testcase.ports import (
    IRunTestCasesCommandHandler, RunTestCaseCommand, IDataPlatformFactory, INotifier,
)
from src.dtos import TestCaseResultDTO, TestResult, TestStatus
from src.testcase.testcases import TestCaseFactory, TestCaseUnknownError


class RunTestCasesCommandHandler(IRunTestCasesCommandHandler):
    """Receives a command and executes testcases"""

    def __init__(self, backend_factory: IDataPlatformFactory, notifiers: List[INotifier]):
        self.backend_factory: IDataPlatformFactory = backend_factory
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
