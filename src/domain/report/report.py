from typing import List, Dict, Tuple

from src.infrastructure_ports import IDtoStorage
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
    ObjectType,
)


class ReportError(Exception):
    """
    Exception raised when a report operation fails.
    """


class ReportArtifactNotSpecifiedError(ReportError):
    """
    Exception raised when artifact is not specified for TestCaseReportDTO
    """


class WrongReportTypeError(ReportError):
    """
    Exception raised when a report is not of the expected type
    """


class UnknownReportTypeError(ReportError):
    """
    Exception raised when a report type is unknown
    """


class NoFormatterFoundError(ReportError):
    """
    Exception raised when no formatter is found for a given report type,
    artifact and format
    """


class ReportNotRetrievableError(ReportError):
    """
    Exception raised when a report is not retrievable
    """


class Report:
    """
    Handles report creation, storage and retrieval.
    """

    formatters_by_type_artifact_and_format: Dict[
        Tuple[
            ReportType, ReportArtifact, ReportArtifactFormat
        ],
        IReportFormatter,
    ]

    def __init__(
        self,
        formatters: List[IReportFormatter],
        dto_storage: IDtoStorage,
    ):
        self.formatters = formatters
        self.dto_storage = dto_storage
        self.formatters_by_type_artifact_and_format: Dict[
            Tuple[
                ReportType, ReportArtifact, ReportArtifactFormat
            ],
            IReportFormatter,
        ] = {}

        for formatter in self.formatters:
            key = (
                formatter.report_type,
                formatter.report_artifact,
                formatter.artifact_format,
            )
            if key in self.formatters_by_type_artifact_and_format:
                raise ReportError(
                    f"Formatter {formatter} already registered"
                )
            self.formatters_by_type_artifact_and_format[key] = formatter

    # TODO: split in create_testcase_report and create_testrun_report
    def create_report(self, result: TestDTO) -> TestReportDTO:
        """Creates a report for a given result"""

        report: TestCaseReportDTO | TestRunReportDTO
        if isinstance(result, TestRunDTO):
            report = TestRunReportDTO.from_testrun_result(result)
            result.report_id = report.report_id
            return report
        elif isinstance(result, TestCaseDTO):
            report = TestCaseReportDTO.from_testcase_result(result)
            result.report_id = report.report_id
            return report
        else:
            raise WrongReportTypeError(
                f"Wrong report type: {type(result)}"
            )

    #TODO: split in load_testcase_report and load_testrun_report
    def retrieve_report(
        self, report_id: str, report_type: ReportType
    ) -> TestReportDTO:
        """Retrieves a testcase or testrun report from internal storage"""

        if report_type == ReportType.TESTCASE:
            object_type = ObjectType.TESTCASE_REPORT
        elif report_type == ReportType.TESTRUN:
            object_type = ObjectType.TESTRUN_REPORT
        else:
            raise UnknownReportTypeError(
                f"Invalid report type: {report_type}"
            )

        report_dto = self.dto_storage.read_dto(
            object_type=object_type,
            id=report_id,
        )

        if report_type == ReportType.TESTCASE:
            expected_type = TestCaseReportDTO
        else:
            expected_type = TestRunReportDTO
        if not isinstance(report_dto, expected_type):
            raise ReportNotRetrievableError(
                f"Couldn't retrieve report {report_id}"
            )

        return report_dto

    # TODO: split in create_testcase_report_artifact and create_testrun_report_artifact
    def create_artifact(
        self,
        report: TestReportDTO,
        artifact_format: ReportArtifactFormat,
        artifact: ReportArtifact | None = None,
    ) -> bytes:
        """
        Formats a report artifact for a given report.
        """

        if isinstance(report, TestRunReportDTO):
            artifact = ReportArtifact.REPORT
            report_type = ReportType.TESTRUN
        elif isinstance(report, TestCaseReportDTO):
            report_type = ReportType.TESTCASE
            if artifact is None:
                msg = (
                    "Artifact (report or diff) must be specified "
                    "for TestCaseReportDTO"
                )
                raise ReportArtifactNotSpecifiedError(msg)
        else:
            raise WrongReportTypeError(
                f"Wrong report type: {type(report)}"
            )

        key = (report_type, artifact, artifact_format)
        formatter = (
            self.formatters_by_type_artifact_and_format.get(key)
        )
        if formatter is None:
            msg = f"Formatter for {key} not registered"
            raise NoFormatterFoundError(msg)
        artifact_bytes = formatter.create_artifact(report)

        return artifact_bytes

    def save_report(self, report: TestReportDTO) -> None:
        """Saves an internal report to structured storage"""

        if not isinstance(
            report, (TestCaseReportDTO, TestRunReportDTO)
        ):
            raise WrongReportTypeError(
                f"Unsupported report type: {type(report)}"
            )

        self.dto_storage.write_dto(dto=report)
