from typing import List, Dict, Tuple, cast

from src.infrastructure_ports import IDtoStorage, INotifier
from src.domain.report.plugins import IReportFormatter
from src.dtos import (
    TestCaseReportDTO,
    TestRunReportDTO,
    TestCaseDTO,
    TestRunDTO,
    TestReportDTO,
    ReportArtifact,
    ReportArtifactFormat,
    ReportType,
    ObjectType,
    Importance,
    NotificationDTO,
    NotificationProcess,
)


class ReportError(Exception):
    """Exception raised when a report operation fails."""


class NoFormatterFoundError(ReportError):
    """Exception raised when no formatter is found for a given
    report type, artifact and format."""


class ReportNotRetrievableError(ReportError):
    """Exception raised when a report is not retrievable."""


class Report:
    """Handles report creation, storage and retrieval."""

    formatters_by_type_artifact_and_format: Dict[
        Tuple[ReportType, ReportArtifact, ReportArtifactFormat],
        IReportFormatter,
    ]

    def __init__(
        self,
        formatters: List[IReportFormatter],
        dto_storage: IDtoStorage,
        notifiers: List[INotifier] | None = None,
    ):
        self.formatters = formatters
        self.dto_storage = dto_storage
        self.notifiers: List[INotifier] = notifiers or []
        self.formatters_by_type_artifact_and_format: Dict[
            Tuple[ReportType, ReportArtifact, ReportArtifactFormat],
            IReportFormatter,
        ] = {}

        for formatter in self.formatters:
            key = (
                formatter.report_type,
                formatter.report_artifact,
                formatter.artifact_format,
            )
            if key in self.formatters_by_type_artifact_and_format:
                raise ReportError(f"Formatter {formatter} already registered")
            self.formatters_by_type_artifact_and_format[key] = formatter

    def _notify(
        self,
        message: str,
        domain: str = "",
        importance: Importance = Importance.INFO,
    ):
        notification = NotificationDTO(
            domain=domain,
            process=NotificationProcess.REPORT,
            importance=importance,
            message=message,
        )
        for notifier in self.notifiers:
            notifier.notify(notification)

    def create_testcase_report(self, result: TestCaseDTO) -> TestCaseReportDTO:
        """Creates a report from a testcase result."""
        report = TestCaseReportDTO.from_testcase_result(result)
        result.report_id = report.report_id
        return report

    def create_testrun_report(self, result: TestRunDTO) -> TestRunReportDTO:
        """Creates a report from a testrun result."""
        report = TestRunReportDTO.from_testrun_result(result)
        result.report_id = report.report_id
        return report

    def load_testcase_report(self, report_id: str) -> TestCaseReportDTO:
        """Loads a testcase report from internal storage."""
        report_dto = self.dto_storage.read_dto(
            object_type=ObjectType.TESTCASE_REPORT, id=report_id
        )
        if not isinstance(report_dto, TestCaseReportDTO):
            raise ReportNotRetrievableError(f"Couldn't retrieve tc report {report_id}")
        return report_dto

    def load_testrun_report(self, report_id: str) -> TestRunReportDTO:
        """Loads a testrun report from internal storage."""
        report_dto = self.dto_storage.read_dto(
            object_type=ObjectType.TESTRUN_REPORT, id=report_id
        )
        if not isinstance(report_dto, TestRunReportDTO):
            raise ReportNotRetrievableError(f"Couldn't retrieve tr report {report_id}")
        return report_dto

    def list_testcase_reports(
        self,
        domain: str,
        testrun_id: str | None = None,
        date: str | None = None,
    ) -> List[TestCaseReportDTO]:
        """Lists testcase reports by domain, optionally filtered
        by testrun_id and date."""

        filters: Dict[str, str] = {"domain": domain}
        if testrun_id is not None:
            filters["testrun_id"] = testrun_id
        if date is not None:
            filters["date"] = date
        dtos = self.dto_storage.list_dtos(
            object_type=ObjectType.TESTCASE_REPORT, filters=filters
        )
        return [cast(TestCaseReportDTO, dto) for dto in dtos]

    def list_testrun_reports(
        self, domain: str, date: str | None = None
    ) -> List[TestRunReportDTO]:
        """Lists testrun reports by domain, optionally filtered by date."""

        filters: Dict[str, str] = {"domain": domain}
        if date is not None:
            filters["date"] = date
        dtos = self.dto_storage.list_dtos(
            object_type=ObjectType.TESTRUN_REPORT, filters=filters
        )
        return [cast(TestRunReportDTO, dto) for dto in dtos]

    def create_testcase_report_artifact(
        self,
        report: TestCaseReportDTO,
        artifact: ReportArtifact,
        artifact_format: ReportArtifactFormat,
    ) -> bytes:
        """Creates an artifact for a testcase report."""
        key = (ReportType.TESTCASE, artifact, artifact_format)
        formatter = self.formatters_by_type_artifact_and_format.get(key)
        if formatter is None:
            raise NoFormatterFoundError(f"Formatter for {key} not registered")
        return formatter.create_artifact(report)

    def create_testrun_report_artifact(
        self, report: TestRunReportDTO, artifact_format: ReportArtifactFormat
    ) -> bytes:
        """Creates an artifact for a testrun report."""
        key = (ReportType.TESTRUN, ReportArtifact.REPORT, artifact_format)
        formatter = self.formatters_by_type_artifact_and_format.get(key)
        if formatter is None:
            raise NoFormatterFoundError(f"Formatter for {key} not registered")
        return formatter.create_artifact(report)

    def save_report(self, report: TestReportDTO) -> None:
        """Saves an internal report to structured storage."""
        if not isinstance(report, (TestCaseReportDTO, TestRunReportDTO)):
            raise ReportError(f"Unsupported report type: {type(report)}")
        self.dto_storage.write_dto(dto=report)

    def create_and_save_all_reports(self, testrun: TestRunDTO) -> TestRunReportDTO:
        """Creates and saves all reports for a testrun and its testcases,
        then saves the testrun with updated report_ids."""
        self._notify(
            f"Creating reports for testrun {testrun.testrun_id}",
            domain=testrun.domain,
        )
        testrun_report = self.create_testrun_report(testrun)
        self.save_report(testrun_report)
        self._notify("Testrun report created and saved", domain=testrun.domain)

        for testcase in testrun.testcase_results:
            testcase_report = self.create_testcase_report(testcase)
            self.save_report(testcase_report)
            self._notify(
                f"Testcase report created for {testcase.testobject.name}",
                domain=testrun.domain,
            )

        self.dto_storage.write_dto(dto=testrun)
        n = len(testrun.testcase_results)
        self._notify(
            f"All reports created and saved ({n} testcase report(s))",
            domain=testrun.domain,
        )
        return testrun_report
