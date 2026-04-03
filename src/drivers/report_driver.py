from typing import List

from pydantic import UUID4

from src.dtos import (
    TestCaseReportDTO,
    TestRunReportDTO,
    TestReportDTO,
    TestCaseDTO,
    TestRunDTO,
    ReportArtifact,
    ReportArtifactFormat,
)
from src.domain_ports import (
    IReport,
    CreateTestCaseReportCommand,
    CreateTestRunReportCommand,
    SaveReportCommand,
    ListTestCaseReportsCommand,
    ListTestRunReportsCommand,
    CreateTestCaseReportArtifactCommand,
    CreateTestRunReportArtifactCommand,
    CreateAndSaveAllReportsCommand,
)


class ReportDriver:
    def __init__(self, report_handler: IReport):
        self.report_handler = report_handler

    def create_testcase_report(self, result: TestCaseDTO) -> TestCaseReportDTO:
        """Creates a report from a testcase result."""
        command = CreateTestCaseReportCommand(result=result)
        return self.report_handler.create_testcase_report(command=command)

    def create_testrun_report(self, result: TestRunDTO) -> TestRunReportDTO:
        """Creates a report from a testrun result."""
        command = CreateTestRunReportCommand(result=result)
        return self.report_handler.create_testrun_report(command=command)

    def save_report(self, report: TestReportDTO) -> None:
        """Saves report to internal storage."""
        command = SaveReportCommand(report=report)
        self.report_handler.save_report(command=command)

    def list_testcase_reports(
        self,
        domain: str,
        testrun_id: UUID4 | None = None,
        date: str | None = None,
    ) -> List[TestCaseReportDTO]:
        """Lists testcase reports by domain."""
        command = ListTestCaseReportsCommand(
            domain=domain, testrun_id=testrun_id, date=date
        )
        return self.report_handler.list_testcase_reports(command=command)

    def list_testrun_reports(
        self, domain: str, date: str | None = None
    ) -> List[TestRunReportDTO]:
        """Lists testrun reports by domain."""
        command = ListTestRunReportsCommand(domain=domain, date=date)
        return self.report_handler.list_testrun_reports(command=command)

    def create_testcase_report_artifact(
        self,
        report_id: UUID4,
        artifact: ReportArtifact,
        artifact_format: ReportArtifactFormat,
    ) -> bytes:
        """Creates an artifact for a testcase report."""
        command = CreateTestCaseReportArtifactCommand(
            report_id=report_id,
            artifact=artifact,
            artifact_format=artifact_format,
        )
        return self.report_handler.create_testcase_report_artifact(command=command)

    def create_testrun_report_artifact(
        self, report_id: UUID4, artifact_format: ReportArtifactFormat
    ) -> bytes:
        """Creates an artifact for a testrun report."""
        command = CreateTestRunReportArtifactCommand(
            report_id=report_id, artifact_format=artifact_format
        )
        return self.report_handler.create_testrun_report_artifact(command=command)

    def create_and_save_all_reports(self, testrun: TestRunDTO) -> TestRunReportDTO:
        """Creates and saves all reports for a testrun and its testcases."""
        command = CreateAndSaveAllReportsCommand(testrun=testrun)
        return self.report_handler.create_and_save_all_reports(command=command)
