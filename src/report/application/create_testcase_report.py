from src.report.testcase_report import TestCaseReport
from src.dtos import TestCaseReportDTO
from src.report.ports import (
    ICreateTestCaseReportCommandHandler,
    CreateTestCaseReportCommand,
    IReportFormatter,
)


class CreateTestCaseReportCommandHandler(ICreateTestCaseReportCommandHandler):
    """Creates testcase report, populates artifacts and returns as dto"""

    def __init__(self, formatter: IReportFormatter):
        self.formatter: IReportFormatter = formatter

    def create(self, command: CreateTestCaseReportCommand) -> TestCaseReportDTO:

        report = TestCaseReport(result=command.testcase_result)
        report.create_artifacts(tags=command.tags, formatter=self.formatter)

        return report.to_dto()
