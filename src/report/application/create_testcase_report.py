from src.report.testcase_report import TestCaseReport
from src.dtos import TestCaseReportDTO
from src.report.ports import (
    ICreateTestCaseReportCommandHandler, CreateTestCaseReportCommand,
    IReportFormatter, IStorage, IReportNamingConventions
)


class CreateTestCaseReportCommandHandler(ICreateTestCaseReportCommandHandler):

    def __init__(self, formatter: IReportFormatter, storage: IStorage,
                 naming_conventions: IReportNamingConventions):

        self.formatter: IReportFormatter = formatter
        self.storage: IStorage = storage
        self.naming_conventions: IReportNamingConventions = naming_conventions

    def create(self, command: CreateTestCaseReportCommand) -> TestCaseReportDTO:

        report = TestCaseReport.from_testcase_result(
            testcase_result=command.testcase_result,
            formatter=self.formatter,
            storage=self.storage,
            naming_conventions=self.naming_conventions,
        )
        formatted_report = report.format_report(format=command.format)

        return formatted_report.to_dto()
