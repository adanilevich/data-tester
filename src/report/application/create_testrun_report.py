from src.report.testrun_report import TestRunReport
from src.dtos import TestRunReportDTO
from src.report.ports import (
    CreateTestRunReportCommand, ICreateTestRunReportCommandHandler,
    IReportFormatter
)


class CreateTestRunReportCommandHandler(ICreateTestRunReportCommandHandler):

    def __init__(self, formatter: IReportFormatter):
        self.formatter: IReportFormatter = formatter

    def create(self, command: CreateTestRunReportCommand) -> TestRunReportDTO:

        report = TestRunReport.from_testrun_result(command.testrun_result)
        report.format_report(format=command.format, formatter=self.formatter)

        return report.to_dto()
