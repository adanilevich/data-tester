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
        self, create_testcase_report_handler: ICreateTestCaseReportCommandHandler,
        create_testrun_report_handler: ICreateTestRunReportCommandHandler,
        save_report_handler: ISaveReportCommandHandler,):

        self.create_testcase_report_handler = create_testcase_report_handler
        self.create_testrun_report_handler = create_testrun_report_handler
        self.save_report_handler = save_report_handler

    def create_testcase_report(
        self, testcase_result: TestCaseResultDTO, format: str,) -> TestCaseReportDTO:

        command = CreateTestCaseReportCommand(
            testcase_result=testcase_result,
            format=format
        )

        report = self.create_testcase_report_handler.create(command=command)

        return report

    def create_testrun_report(
        self, testcase_results: List[TestCaseResultDTO],
        format: str,) -> TestRunReportDTO:

        command = CreateTestRunReportCommand(
            testrun_result=TestRunResultDTO.from_testcase_results(testcase_results),
            format=format
        )

        report = self.create_testrun_report_handler.create(command=command)

        return report

    def save_report(
        self, report: TestCaseReportDTO | TestRunReportDTO, location: str,
        group_by: List[str]):

        command = SaveReportCommand(
            report=report,
            location=location,
            group_by=group_by,
        )

        self.save_report_handler.save(command=command)
