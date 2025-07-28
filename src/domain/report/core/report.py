from typing import List, Dict, Tuple, cast

from src.infrastructure.storage import IStorageFactory
from src.domain.report.plugins import IReportFormatter
from src.dtos import (
    TestCaseReportDTO,
    TestRunReportDTO,
    TestCaseDTO,
    TestRunDTO,
    TestDTO,
    ReportArtifact,
    ReportArtifactFormat,
    ReportType,
    TestReportDTO,
    LocationDTO,
    StorageObject,
)


class NoFormatterFoundError(Exception):
    """Raised when no formatter is found for a given report type, artifact and format"""


class ReportArtifactNotSpecifiedError(Exception):
    """Raised when artifact is not specified for TestCaseReportDTO"""


class WrongReportTypeError(Exception):
    """Raised when a report is not of the expected type"""


class Report:
    """
    Abstact report class from which TestRunReport and TestCaseReport inherit.
    Bundles common functions like creating and saving artifacts.
    """

    formatters_by_type_artifact_and_format: Dict[
        Tuple[ReportType, ReportArtifact, ReportArtifactFormat], IReportFormatter
    ]

    def __init__(
        self, formatters: List[IReportFormatter], storage_factory: IStorageFactory
    ):
        self.formatters = formatters
        self.storage_factory = storage_factory
        self.formatters_by_type_artifact_and_format: Dict[
            Tuple[ReportType, ReportArtifact, ReportArtifactFormat], IReportFormatter
        ] = {}

        for formatter in self.formatters:
            key = (
                formatter.report_type,
                formatter.report_artifact,
                formatter.artifact_format,
            )
            if key in self.formatters_by_type_artifact_and_format:
                raise ValueError(f"Formatter {formatter} already registered")
            self.formatters_by_type_artifact_and_format[key] = formatter

    def create_report(self, result: TestDTO) -> TestReportDTO:
        """Creates a report for a given result"""

        report: TestCaseReportDTO | TestRunReportDTO
        if isinstance(result, TestRunDTO):
            report = TestRunReportDTO.from_testrun(result)
            result.report_id = report.report_id
            return report
        elif isinstance(result, TestCaseDTO):
            report = TestCaseReportDTO.from_testcase_result(result)
            result.report_id = report.report_id
            return report
        else:
            raise WrongReportTypeError(f"Wrong report type: {type(result)}")

    def retrieve_report(
        self, location: LocationDTO, report_id: str, report_type: ReportType
    ) -> TestReportDTO:
        """Retrieves a testcase or testrun report from internal structured storage"""

        storage = self.storage_factory.get_storage(location)

        if report_type == ReportType.TESTCASE:
            object_type = StorageObject.TESTCASE_REPORT
        elif report_type == ReportType.TESTRUN:
            object_type = StorageObject.TESTRUN_REPORT
        else:
            raise ValueError(f"Invalid report type: {report_type}")

        report_dto = storage.read(
            object_type=object_type,
            object_id=report_id,
            location=location,
        )

        try:
            if report_type == ReportType.TESTCASE:
                return cast(TestCaseReportDTO, report_dto)
            elif report_type == ReportType.TESTRUN:
                return cast(TestRunReportDTO, report_dto)
        except Exception:
            pass

        raise ValueError(f"Couldn't retrieve report {report_id} as {report_type}")

    def create_artifact(
        self,
        report: TestReportDTO,
        artifact_format: ReportArtifactFormat,
        artifact: ReportArtifact | None = None,
    ) -> bytes:
        """
        Formats a report artifact for a given report.

        Args:
            report: TestReportDTO can be either TestRunReportDTO or TestCaseReportDTO
            artifact_format: ReportArtifactFormat
            artifact: ReportArtifact | None = None must be specified as diff or report
                in order to create a testcase report artifact. For TestRunReportDTO,
                artifact is not required and will be set to ReportArtifact.REPORT.

        Returns:
            bytes: The formatted artifact

        Raises:
            ReportArtifactNotSpecifiedError: When artifact (report or diff) is not
            specified for TestCaseReportDTO
                WrongReportTypeError: When report is not of the expected type
            NoFormatterFoundError: When no formatter is found for a given
                report type, artifact and format
        """

        if isinstance(report, TestRunReportDTO):
            artifact = ReportArtifact.REPORT
            report_type = ReportType.TESTRUN
        elif isinstance(report, TestCaseReportDTO):
            report_type = ReportType.TESTCASE
            if artifact is None:
                msg = "Artifact (report or diff) must be specified for TestCaseReportDTO"
                raise ReportArtifactNotSpecifiedError(msg)
        else:
            raise WrongReportTypeError(f"Wrong report type: {type(report)}")

        key = (report_type, artifact, artifact_format)
        formatter = self.formatters_by_type_artifact_and_format.get(key)
        if formatter is None:
            msg = f"Formatter for {key} not registered"
            raise NoFormatterFoundError(msg)
        artifact_bytes = formatter.create_artifact(report)

        return artifact_bytes

    def save_report(self, location: LocationDTO, report: TestReportDTO) -> None:
        """Saves an internal report to structured storage"""

        storage = self.storage_factory.get_storage(location)

        # Determine object type based on report type
        if isinstance(report, TestCaseReportDTO):
            object_type = StorageObject.TESTCASE_REPORT
        elif isinstance(report, TestRunReportDTO):
            object_type = StorageObject.TESTRUN_REPORT
        else:
            raise ValueError(f"Unsupported report type: {type(report)}")

        storage.write(dto=report, object_type=object_type, location=location)

    def save_artifact(self, location: LocationDTO, artifact: bytes) -> None:
        """Saves a user report artifact as bytes"""

        storage = self.storage_factory.get_storage(location)
        storage.write_bytes(content=artifact, location=location)

        return None
