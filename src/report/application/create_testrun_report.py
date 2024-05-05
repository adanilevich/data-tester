from src.report.testrun_report import TestRunReport
from src.dtos import TestRunReportDTO
from src.report.ports import (
    CreateTestRunReportCommand,
    ICreateTestRunReportCommandHandler,
    IReportFormatter,
)


class CreateTestRunReportCommandHandler(ICreateTestRunReportCommandHandler):
    """Creates a testrun report, populates report artifacts and returns as dto"""

    def __init__(self, formatter: IReportFormatter):
        self.formatter: IReportFormatter = formatter

    def create(self, command: CreateTestRunReportCommand) -> TestRunReportDTO:
        report = TestRunReport(result=command.testrun_result)
        report.create_artifacts(tags=command.tags, formatter=self.formatter)

        return report.to_dto()
