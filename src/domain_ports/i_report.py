from abc import ABC, abstractmethod
from typing import List

from pydantic import UUID4

from src.dtos.testcase_dtos import TestCaseDTO, TestRunDTO
from src.dtos import (
    DTO,
    TestCaseReportDTO,
    TestRunReportDTO,
    TestReportDTO,
    ReportArtifact,
    ReportArtifactFormat,
)


class CreateTestCaseReportCommand(DTO):
    result: TestCaseDTO


class CreateTestRunReportCommand(DTO):
    result: TestRunDTO


class SaveReportCommand(DTO):
    report: TestReportDTO


class LoadTestCaseReportCommand(DTO):
    report_id: UUID4


class LoadTestRunReportCommand(DTO):
    report_id: UUID4


class ListTestCaseReportsCommand(DTO):
    domain: str
    testrun_id: UUID4 | None = None
    date: str | None = None


class ListTestRunReportsCommand(DTO):
    domain: str
    date: str | None = None


class CreateTestCaseReportArtifactCommand(DTO):
    report_id: UUID4
    artifact: ReportArtifact
    artifact_format: ReportArtifactFormat


class CreateTestRunReportArtifactCommand(DTO):
    report_id: UUID4
    artifact_format: ReportArtifactFormat


class CreateAndSaveAllReportsCommand(DTO):
    testrun: TestRunDTO


class IReport(ABC):
    @abstractmethod
    def create_testcase_report(
        self, command: CreateTestCaseReportCommand
    ) -> TestCaseReportDTO:
        """Creates a report from a testcase result."""

    @abstractmethod
    def create_testrun_report(
        self, command: CreateTestRunReportCommand
    ) -> TestRunReportDTO:
        """Creates a report from a testrun result."""

    @abstractmethod
    def save_report(self, command: SaveReportCommand) -> None:
        """Saves report in application-internal storage."""

    @abstractmethod
    def load_testcase_report(
        self, command: LoadTestCaseReportCommand
    ) -> TestCaseReportDTO:
        """Loads a testcase report from internal storage."""

    @abstractmethod
    def load_testrun_report(self, command: LoadTestRunReportCommand) -> TestRunReportDTO:
        """Loads a testrun report from internal storage."""

    @abstractmethod
    def list_testcase_reports(
        self, command: ListTestCaseReportsCommand
    ) -> List[TestCaseReportDTO]:
        """Lists testcase reports by domain, optionally filtered
        by testrun_id and date."""

    @abstractmethod
    def list_testrun_reports(
        self, command: ListTestRunReportsCommand
    ) -> List[TestRunReportDTO]:
        """Lists testrun reports by domain, optionally filtered by date."""

    @abstractmethod
    def create_testcase_report_artifact(
        self, command: CreateTestCaseReportArtifactCommand
    ) -> bytes:
        """Loads a testcase report and creates the requested artifact."""

    @abstractmethod
    def create_testrun_report_artifact(
        self, command: CreateTestRunReportArtifactCommand
    ) -> bytes:
        """Loads a testrun report and creates the requested artifact."""

    @abstractmethod
    def create_and_save_all_reports(
        self, command: CreateAndSaveAllReportsCommand
    ) -> TestRunReportDTO:
        """Creates and saves all reports for a testrun and its testcases,
        then saves the testrun with updated report_ids."""
