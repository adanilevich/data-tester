from uuid import UUID

from src.domain_ports import (
    CreateTestCaseReportArtifactCommand,
    CreateTestRunReportArtifactCommand,
    IReport,
)
from src.dtos import ReportArtifact, ReportArtifactFormat


class ReportDriver:
    def __init__(self, report_adapter: IReport):
        self.adapter = report_adapter

    def create_testcase_report_artifact(
        self,
        testcase_id: UUID,
        artifact: ReportArtifact,
        artifact_format: ReportArtifactFormat,
    ) -> bytes:
        command = CreateTestCaseReportArtifactCommand(
            testcase_id=testcase_id,
            artifact=artifact,
            artifact_format=artifact_format,
        )
        return self.adapter.create_testcase_report_artifact(command=command)

    def create_testrun_report_artifact(
        self,
        testrun_id: UUID,
        artifact_format: ReportArtifactFormat,
    ) -> bytes:
        command = CreateTestRunReportArtifactCommand(
            testrun_id=testrun_id,
            artifact_format=artifact_format,
        )
        return self.adapter.create_testrun_report_artifact(command=command)
