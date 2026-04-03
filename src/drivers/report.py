from src.dtos import TestReportDTO, TestDTO
from src.domain_ports import (
    IReportCommandHandler,
    CreateReportCommand,
    SaveReportCommand,
)


class ReportDriver:
    #TODO: implement list_testcase_reports, list_testrun_reports
    #TODO: implement create_testcase_report_artifact
    #TODO: implement create_testrun_report_artifact
    def __init__(self, report_handler: IReportCommandHandler):
        self.report_handler = report_handler

    def create_report(
        self, result: TestDTO
    ) -> TestReportDTO:
        """Creates testcase or testrun report"""

        command = CreateReportCommand(result=result)
        report = self.report_handler.create_report(
            command=command
        )

        return report

    def save_report(
        self, report: TestReportDTO
    ) -> None:
        """Saves report to internal storage."""

        command = SaveReportCommand(report=report)
        self.report_handler.save_report(command=command)
