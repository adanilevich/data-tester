from typing import List, Dict, Tuple
import json

from src.storage.i_storage import IStorage, StorageTypeUnknownError
from src.report.ports import IReportFormatter
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
    Store,
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

    storages_by_type: Dict[Store, IStorage]
    formatters_by_type_artifact_and_format: Dict[
        Tuple[ReportType, ReportArtifact, ReportArtifactFormat], IReportFormatter
    ]

    def __init__(self, formatters: List[IReportFormatter], storages: List[IStorage]):
        self.formatters = formatters
        self.storages = storages
        self.storages_by_type: Dict[Store, IStorage] = {}
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

        for storage in storages:
            for storage_type in storage.supported_storage_types:
                if storage_type in self.storages_by_type:
                    raise ValueError(f"Storage type {storage_type} already registered")
                self.storages_by_type[storage_type] = storage

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

    def retrieve_report(self, location: LocationDTO) -> TestReportDTO:
        """Retrieves a testcase report from a given location"""

        storage = self.storages_by_type.get(location.store)
        if storage is None:
            raise StorageTypeUnknownError(f"Storage type {location.store} not supported")

        report_as_dict_bytes = storage.read(location)
        report_as_dict = json.loads(report_as_dict_bytes)

        # try to initialize one of the both report types from the dict
        report: TestCaseReportDTO | TestRunReportDTO | None = None
        try:
            report = TestCaseReportDTO.from_dict(report_as_dict)
        except Exception:
            pass
        try:
            report = TestRunReportDTO.from_dict(report_as_dict)
        except Exception:
            pass

        if report is None:
            msg = "Couldn't initialize TestRunReportDTO or TestCaseReportDTO from dict"
            raise ValueError(msg)

        return report

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

    def save_artifact(self, location: LocationDTO, artifact: bytes) -> None:
        """Saves a report artifact to a given location"""

        storage = self.storages_by_type.get(location.store)
        if storage is None:
            raise StorageTypeUnknownError(f"Storage type {location.store} not supported")

        storage.write(content=artifact, path=location)

        return None
