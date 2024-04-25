from typing import List
from src.report.ports import (
    ISaveReportCommandHandler, SaveReportCommand,
    ICreateTestRunReportCommandHandler, CreateTestRunReportCommand,
    ICreateTestCaseReportCommandHandler, CreateTestCaseReportCommand,
)
from src.dtos import (
    TestCaseResultDTO, TestRunResultDTO, TestCaseReportDTO, TestRunReportDTO
)


class SimpleReportManager:

    def __init__(
        self,
        testcase_handler: ICreateTestCaseReportCommandHandler,
        testrun_handler: ICreateTestRunReportCommandHandler,
        storage_handler: ISaveReportCommandHandler,
    ):
        self.testcase_handler = testcase_handler
        self.testrun_handler = testrun_handler
        self.storage_handler = storage_handler

    def create_testcase_report(
        self,
        testcase_result: TestCaseResultDTO,
        format: str,
    ) -> TestCaseReportDTO:

        command = CreateTestCaseReportCommand(
            testcase_result=testcase_result,
            format=format
        )

        report = self.testcase_handler.create(command=command)

        return report

    def create_testrun_report(
        self,
        testcase_results: List[TestCaseResultDTO],
        format: str,
    ) -> TestRunReportDTO:

        command = CreateTestRunReportCommand(
            testrun_result=TestRunResultDTO.from_testcase_results(testcase_results),
            format=format
        )

        report = self.testrun_handler.create(command=command)

        return report

    def save_report(
            self,
            report: TestCaseReportDTO | TestRunReportDTO,
            location: str,
            group_by: List[str]
    ):

        command = SaveReportCommand(
            report=report,
            location=location,
            group_by=group_by,
        )

        self.storage_handler.save(command=command)
