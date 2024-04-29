from src.report.testrun_report import TestRunReport
from src.dtos import TestRunReportDTO
from src.report.ports import (
    CreateTestRunReportCommand, ICreateTestRunReportCommandHandler,
    IReportFormatter, IStorage, IReportNamingConventions
)


class CreateTestRunReportCommandHandler(ICreateTestRunReportCommandHandler):

    def __init__(self, formatter: IReportFormatter, storage: IStorage,
                 naming_conventions: IReportNamingConventions):

        self.formatter: IReportFormatter = formatter
        self.storage: IStorage = storage
        self.naming_conventions: IReportNamingConventions = naming_conventions

    def create(self, command: CreateTestRunReportCommand) -> TestRunReportDTO:

        report = TestRunReport.from_testrun_result(
            testrun_result=command.testrun_result,
            formatter=self.formatter,
            storage=self.storage,
            naming_conventions=self.naming_conventions,
        )
        formatted_report = report.format_report(format=command.format)

        return formatted_report.to_dto()
