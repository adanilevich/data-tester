from src.report.ports import (
    SaveReportCommand, ISaveReportCommandHandler, IStorage, IReportNamingConventions,
)
from src.report import TestCaseReport, TestRunReport
from src.dtos import TestCaseReportDTO, TestRunReportDTO


class SaveReportCommandHandler(ISaveReportCommandHandler):

    def __init__(self, storage: IStorage, naming_conventions: IReportNamingConventions,):

        self.storage: IStorage = storage
        self.naming_conventions: IReportNamingConventions = naming_conventions

    def save(self, command: SaveReportCommand):

        report: TestCaseReport | TestRunReport

        if isinstance(command.report, TestCaseReportDTO):
            report = TestCaseReport.from_dto(report_dto=command.report,)
        elif isinstance(command.report, TestRunReportDTO):
            report = TestRunReport.from_dto(report_dto=command.report)
        else:
            raise ValueError(f"Unknows report class {command.report.__class_}")

        report.save(
            location=command.location,
            group_by=command.group_by,
            storage=self.storage,
            naming_conventions=self.naming_conventions
        )
