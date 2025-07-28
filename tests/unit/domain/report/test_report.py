from unittest.mock import Mock

import pytest

from src.domain.report.core.report import (
    Report,
    NoFormatterFoundError,
    ReportArtifactNotSpecifiedError,
    WrongReportTypeError,
)
from src.domain.report.plugins import (
    TxtTestCaseReportFormatter,
    XlsxTestRunReportFormatter,
    XlsxTestCaseDiffFormatter,
)
from src.dtos import (
    TestCaseReportDTO,
    TestRunReportDTO,
    ReportArtifact,
    ReportArtifactFormat,
    LocationDTO,
    ReportType,
)
from src.infrastructure.storage import (
    StorageFactory,
    FormatterFactory,
    StorageTypeUnknownError,
)
from src.config import Config


@pytest.fixture
def formatters():
    """Create formatters as defined in config.py"""
    return [
        TxtTestCaseReportFormatter(),
        XlsxTestRunReportFormatter(),
        XlsxTestCaseDiffFormatter(),
    ]


@pytest.fixture
def storage_factory():
    config = Config()
    formatter_factory = FormatterFactory()
    return StorageFactory(config, formatter_factory)


@pytest.fixture
def report(formatters, storage_factory):
    return Report(formatters=formatters, storage_factory=storage_factory)


class TestReport:
    def test_initialization_with_formatters_and_storages(
        self, formatters, storage_factory
    ):
        # given formatters and storage factory
        # when initializing Report with formatters and storage factory
        report = Report(formatters=formatters, storage_factory=storage_factory)

        # then formatters and storages are properly registered
        assert len(report.formatters) == 3
        assert report.storage_factory == storage_factory
        assert len(report.formatters_by_type_artifact_and_format) == 3

    def test_initialization_with_duplicate_formatter(self, storage_factory):
        # given duplicate formatters and correct storage factory
        duplicate_formatters = [
            TxtTestCaseReportFormatter(),
            TxtTestCaseReportFormatter(),
        ]

        # then initialization raises ValueError
        with pytest.raises(ValueError, match="Formatter.*already registered"):
            Report(formatters=duplicate_formatters, storage_factory=storage_factory)  # type: ignore

    def test_create_report_from_testcase_result(self, report, testcase_result):
        # when creating a report from testcase result
        report_dto = report.create_report(testcase_result)

        # then it returns a TestCaseReportDTO
        assert isinstance(report_dto, TestCaseReportDTO)
        assert report_dto.testcase_id == testcase_result.testcase_id
        assert report_dto.testrun_id == testcase_result.testrun_id
        assert report_dto.testobject == testcase_result.testobject.name
        assert report_dto.testtype == testcase_result.testtype.value
        assert report_dto.diff == testcase_result.diff
        assert report_dto.summary == testcase_result.summary
        assert report_dto.facts == testcase_result.facts
        assert report_dto.details == testcase_result.details
        assert report_dto.specifications == testcase_result.specifications
        assert report_dto.result == testcase_result.result.value
        assert report_dto.start_ts == testcase_result.start_ts
        assert report_dto.end_ts == testcase_result.end_ts

    def test_create_report_from_testrun_result(self, report, testrun):
        # when creating a report from testrun result
        report_dto = report.create_report(testrun)

        # then it returns a TestRunReportDTO
        assert isinstance(report_dto, TestRunReportDTO)
        assert report_dto.testrun_id == testrun.testrun_id
        assert report_dto.result == testrun.result.value
        assert report_dto.start_ts == testrun.start_ts
        assert report_dto.end_ts == testrun.end_ts
        assert len(report_dto.testcase_results) == len(testrun.testcase_results)

        # then the testcase results are correctly converted
        for i, testcase_result in enumerate(testrun.testcase_results):
            dto_testcase = report_dto.testcase_results[i]
            assert dto_testcase.testrun_id == testcase_result.testrun_id
            assert dto_testcase.testobject == testcase_result.testobject.name
            assert dto_testcase.testtype == testcase_result.testtype.value
            assert dto_testcase.summary == testcase_result.summary
            assert dto_testcase.result == testcase_result.result.value
            assert dto_testcase.start_ts == testcase_result.start_ts
            assert dto_testcase.end_ts == testcase_result.end_ts

    def test_create_report_with_wrong_type(self, report):
        # given an invalid result type
        invalid_result = Mock()

        # then creating a report raises WrongReportTypeError
        with pytest.raises(WrongReportTypeError, match="Wrong report type"):
            report.create_report(invalid_result)

    def test_save_and_retrieve_report(self, report, testcase_report, testrun_report):
        # given a testcase report and a testrun report and storage location
        location = LocationDTO("dict://reports/")

        # when both reports are saved
        report.save_report(location, testcase_report)
        report.save_report(location, testrun_report)

        # when retrieving both reports
        retrieved_testcase_report = report.retrieve_report(
            location=location,
            report_id=testcase_report.report_id,
            report_type=ReportType.TESTCASE,
        )
        retrieved_testrun_report = report.retrieve_report(
            location=location,
            report_id=testrun_report.report_id,
            report_type=ReportType.TESTRUN,
        )

        # then it returns the correct report
        assert isinstance(retrieved_testcase_report, TestCaseReportDTO)
        assert retrieved_testcase_report.testcase_id == testcase_report.testcase_id
        assert retrieved_testcase_report.testrun_id == testcase_report.testrun_id
        assert retrieved_testrun_report.testrun_id == testrun_report.testrun_id
        assert retrieved_testrun_report.result == testrun_report.result
        assert retrieved_testrun_report.start_ts == testrun_report.start_ts
        assert retrieved_testrun_report.end_ts == testrun_report.end_ts
        assert len(retrieved_testrun_report.testcase_results) == len(
            testrun_report.testcase_results
        )

    def test_retrieve_report_with_unsupported_storage(self, report, testcase_report):
        # given an unsupported storage type
        location = LocationDTO("unknown://test_reports/")

        # then retrieving raises StorageTypeUnknownError
        with pytest.raises(StorageTypeUnknownError):
            report.retrieve_report(
                location=location,
                report_id=testcase_report.report_id,
                report_type=ReportType.TESTCASE,
            )

    def test_create_artifact_for_testcase_report(self, report, testcase_report):
        # given a testcase report
        # when creating an artifact for the testcase report
        artifact_bytes = report.create_artifact(
            report=testcase_report,
            artifact=ReportArtifact.DIFF,
            artifact_format=ReportArtifactFormat.XLSX,
        )
        # then it returns a bytes object
        assert isinstance(artifact_bytes, bytes)
        # and the artifact is a valid XLSX file
        assert artifact_bytes.startswith(b"PK\x03\x04")

        artifact_bytes = report.create_artifact(
            report=testcase_report,
            artifact=ReportArtifact.REPORT,
            artifact_format=ReportArtifactFormat.TXT,
        )
        artifact_txt = artifact_bytes.decode()
        assert isinstance(artifact_bytes, bytes)
        assert testcase_report.summary in artifact_txt

    def test_create_artifact_for_testrun_report(self, report, testrun_report):
        # given a testrun report
        # when creating an artifact for the testrun report
        artifact_bytes = report.create_artifact(
            report=testrun_report,
            artifact=ReportArtifact.REPORT,
            artifact_format=ReportArtifactFormat.XLSX,
        )
        assert isinstance(artifact_bytes, bytes)
        # and the artifact is a valid XLSX file
        assert artifact_bytes.startswith(b"PK\x03\x04")

    def test_create_artifact_without_artifact_for_testcase(self, report, testcase_report):
        # when creating an artifact for testcase report without specifying artifact
        # then it raises ReportArtifactNotSpecifiedError
        with pytest.raises(
            ReportArtifactNotSpecifiedError, match="Artifact.*must be specified"
        ):
            report.create_artifact(
                report=testcase_report,
                artifact_format=ReportArtifactFormat.JSON,
            )

    def test_create_artifact_with_wrong_report_type(self, report):
        # given an invalid report type
        invalid_report = Mock()

        # then creating an artifact raises WrongReportTypeError
        with pytest.raises(WrongReportTypeError, match="Wrong report type"):
            report.create_artifact(
                report=invalid_report,
                artifact_format=ReportArtifactFormat.JSON,
            )

    def test_create_artifact_with_no_formatter_found(self, report, testcase_report):
        # when creating an artifact with unsupported format
        # then it raises NoFormatterFoundError
        with pytest.raises(NoFormatterFoundError, match="Formatter for.*not registered"):
            report.create_artifact(
                report=testcase_report,
                artifact_format=ReportArtifactFormat.JSON,
                artifact=ReportArtifact.DIFF,  # JSON diff formatter doesn't exist
            )

    def test_save_artifact(self, report):
        # given a testcase report and a testrun report
        location = LocationDTO("dict://test_artifacts/test_artifact.txt")
        artifact_bytes = b"test artifact content"
        # when saving the artifact
        report.save_artifact(location, artifact_bytes)
        # then the artifact is saved
        storage = report.storage_factory.get_storage(location)
        assert storage.read_bytes(location) == artifact_bytes

    def test_save_artifact_with_unsupported_storage(self, report):
        # given an unsupported storage type
        location = LocationDTO("unknown://test_artifact.txt")
        artifact_content = b"test artifact content"

        # then saving raises StorageTypeUnknownError
        with pytest.raises(StorageTypeUnknownError, match="Storage type.*not supported"):
            report.save_artifact(location, artifact_content)
