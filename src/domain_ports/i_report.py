from abc import ABC, abstractmethod

from pydantic import UUID4

from src.dtos import (
    DTO,
    ReportArtifact,
    ReportArtifactFormat,
)


class CreateTestCaseReportArtifactCommand(DTO):
    testcase_id: UUID4
    artifact: ReportArtifact
    artifact_format: ReportArtifactFormat


class CreateTestRunReportArtifactCommand(DTO):
    testrun_id: UUID4
    artifact_format: ReportArtifactFormat


class IReport(ABC):
    @abstractmethod
    def create_testcase_report_artifact(
        self, command: CreateTestCaseReportArtifactCommand
    ) -> bytes:
        """Loads a TestCaseDTO and creates the requested artifact."""

    @abstractmethod
    def create_testrun_report_artifact(
        self, command: CreateTestRunReportArtifactCommand
    ) -> bytes:
        """Loads a TestRunDTO and creates the requested artifact."""
