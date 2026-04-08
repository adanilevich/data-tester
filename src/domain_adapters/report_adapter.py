from typing import List

from src.domain.report.plugins import ITestCaseFormatter, ITestRunFormatter
from src.domain.report.report import Report
from src.domain_ports import (
    CreateTestCaseReportArtifactCommand,
    CreateTestRunReportArtifactCommand,
    IReport,
)
from src.infrastructure_ports import IDtoStorage


class ReportAdapter(IReport):
    """Creates report artifacts by delegating to the Report domain class."""

    def __init__(
        self,
        testcase_formatters: List[ITestCaseFormatter],
        testrun_formatters: List[ITestRunFormatter],
        dto_storage: IDtoStorage,
    ):
        self.report = Report(
            testcase_formatters=testcase_formatters,
            testrun_formatters=testrun_formatters,
            dto_storage=dto_storage,
        )

    def create_testcase_report_artifact(
        self, command: CreateTestCaseReportArtifactCommand
    ) -> bytes:
        return self.report.create_testcase_report_artifact(
            testcase_id=str(command.testcase_id),
            artifact=command.artifact,
            artifact_format=command.artifact_format,
        )

    def create_testrun_report_artifact(
        self, command: CreateTestRunReportArtifactCommand
    ) -> bytes:
        return self.report.create_testrun_report_artifact(
            testrun_id=str(command.testrun_id),
            artifact_format=command.artifact_format,
        )
