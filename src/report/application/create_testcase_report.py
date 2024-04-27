from src.report.testcase_report import TestCaseReport
from src.dtos import TestCaseReportDTO
from src.report.ports import (
    ICreateTestCaseReportCommandHandler, CreateTestCaseReportCommand,
    IReportFormatter
)


class CreateTestCaseReportCommandHandler(ICreateTestCaseReportCommandHandler):

    def __init__(self, formatter: IReportFormatter):
        self.formatter: IReportFormatter = formatter

    def create(self, command: CreateTestCaseReportCommand) -> TestCaseReportDTO:

        report = TestCaseReport.from_testcase_result(command.testcase_result)
        formatted_report = report.format_report(
            format=command.format,
            formatter=self.formatter
        )

        return formatted_report
