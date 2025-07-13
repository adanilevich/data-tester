from abc import ABC, abstractmethod
from typing import Union

from src.dtos.testcase import TestCaseResultDTO, TestRunResultDTO
from src.dtos.report import TestReportDTO, ReportArtifact, ReportArtifactFormat
from src.dtos.dto import DTO


class CreateReportCommand(DTO):
    result: Union[TestCaseResultDTO, TestRunResultDTO]


class SaveReportArtifactsForUsersCommand(DTO):
    report: TestReportDTO
    location: str


class SaveReportCommand(DTO):
    report: TestReportDTO
    location: str


class GetTestCaseReportArtifactCommand(DTO):
    testrun_id: str
    location: str
    testcase_id: str
    artifact: ReportArtifact
    artifact_format: ReportArtifactFormat


class GetTestrunReportArtifactCommand(DTO):
    testrun_id: str
    location: str
    artifact_format: ReportArtifactFormat


class IReportCommandHandler(ABC):
    @abstractmethod
    def create_report(self, command: CreateReportCommand) -> TestReportDTO:
        """
        Creates a report for a given result. Will return a TestRunReportDTO or a
        TestCaseReportDTO based on result type in the command.
        """

    @abstractmethod
    def save_report(self, command: SaveReportCommand) -> None:
        """Saves report in application-internal storage"""

    @abstractmethod
    def get_testcase_report_artifact(
        self, command: GetTestCaseReportArtifactCommand) -> bytes:
        """Returns a report artifact for a given testcase"""

    @abstractmethod
    def get_testrun_report_artifact(
        self, command: GetTestrunReportArtifactCommand) -> bytes:
        """Returns a report artifact for a given testrun"""

    @abstractmethod
    def save_report_artifacts_for_users(
        self, command: SaveReportArtifactsForUsersCommand) -> None:
        """Saves all user-related report artifacts in user-managed locations"""
