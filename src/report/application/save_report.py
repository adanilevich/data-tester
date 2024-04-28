from src.report.ports import (
    SaveReportCommand, ISaveReportCommandHandler, IStorage, IReportNamingConventions,
    IReportFormatter
)
from src.report import TestCaseReport, TestRunReport
from src.dtos import TestCaseReportDTO, TestRunReportDTO


class SaveReportCommandHandler(ISaveReportCommandHandler):

    def __init__(self, storage: IStorage, naming_conventions: IReportNamingConventions,
                 formatter: IReportFormatter):

        self.storage: IStorage = storage
        self.naming_conventions: IReportNamingConventions = naming_conventions
        self.formatter: IReportFormatter

    def save(self, command: SaveReportCommand):

        if isinstance(command.report, TestCaseReportDTO):
            report = TestCaseReport.from_dto(
                report_dto=command.report,
                formatter=self.formatter,
                storage=self.storage,
                naming_conventions=self.naming_conventions,
            )
        elif isinstance(command.report, TestRunReportDTO):
            report = TestRunReport.from_dto(
                report_dto=command.report,
                formatter=self.formatter,
                storage=self.storage,
                naming_conventions=self.naming_conventions,
            )
        else:
            raise ValueError(f"Unknows report class {command.report.__class_}")

        report.save_report(
            location=command.location,
            group_by=command.group_by,
        )
