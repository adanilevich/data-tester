from src.report.ports import (
    SaveReportCommand, ISaveReportCommandHandler, IStorage, IReportNamingConventions
)
from src.report import TestCaseReport, TestRunReport
from src.dtos import TestCaseReportDTO


class SaveReportCommandHandler(ISaveReportCommandHandler):

    def __init__(self, storage: IStorage, naming_conventions: IReportNamingConventions):
        self.storage = storage
        self.naming_conventions = naming_conventions

    def save(self, command: SaveReportCommand):

        if isinstance(command.report, TestCaseReportDTO):
            report = TestCaseReport.from_dto(command.report)
        else:
            report = TestRunReport.from_dto(command.report)

        report.save_report(
            location=command.location,
            group_by=command.group_by,
            naming_conventions=self.naming_conventions,
            storage=self.storage
        )
