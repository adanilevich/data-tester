from typing import List
from datetime import datetime
from uuid import uuid4

from src.testcase.ports import (
    IRunTestCasesCommandHandler, RunTestCaseCommand, IDataPlatformFactory, INotifier,
)
from src.dtos import TestCaseResultDTO, TestResult, TestStatus
from src.testcase.core.testcases import TestCaseFactory, TestCaseUnknownError


class RunTestCasesCommandHandler(IRunTestCasesCommandHandler):
    """Receives a command and executes testcases"""

    def __init__(self, backend_factory: IDataPlatformFactory, notifiers: List[INotifier]):
        self.backend_factory: IDataPlatformFactory = backend_factory
        self.notifiers: List[INotifier] = notifiers

    def run(self, commands: List[RunTestCaseCommand]) -> List[TestCaseResultDTO]:

        results = []
        for command in commands:
            backend_ = self.backend_factory.create(
                domain_config=command.definition.domain_config)
            try:
                testcase = TestCaseFactory.create(
                    definition=command.definition,
                    backend=backend_,
                    notifiers=self.notifiers
                )
                result = testcase.execute()
            except TestCaseUnknownError:
                result = TestCaseResultDTO(
                    testcase_id=uuid4(),
                    result=TestResult.NA,
                    summary=f"Test type {command.definition.testtype} unknown!",
                    facts=[],
                    details=[],
                    status=TestStatus.ERROR,
                    start_ts=datetime.now(),
                    end_ts=datetime.now(),
                    testobject=command.definition.testobject,
                    testrun_id=command.definition.testrun_id,
                    testset_id=command.definition.testset_id,
                    labels=command.definition.labels,
                    diff=dict(),
                    testtype=command.definition.testtype,
                    specifications=command.definition.specs,
                )
            results.append(result)

        return results
