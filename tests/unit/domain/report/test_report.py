from unittest.mock import Mock

import pytest

from src.domain.report import (
    Report,
    NoFormatterFoundError,
    ReportArtifactNotSpecifiedError,
    WrongReportTypeError,
    ReportError,
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
    ReportType,
)
from src.infrastructure.storage.dto_storage_file import MemoryDtoStorage
from src.infrastructure.storage.dto_storage_file import JsonSerializer
from src.dtos import LocationDTO


@pytest.fixture
def formatters():
    """Create formatters as defined in config.py"""
    return [
        TxtTestCaseReportFormatter(),
        XlsxTestRunReportFormatter(),
        XlsxTestCaseDiffFormatter(),
    ]


@pytest.fixture
def dto_storage() -> MemoryDtoStorage:
    return MemoryDtoStorage(
        serializer=JsonSerializer(),
        storage_location=LocationDTO("memory://test/"),
    )


@pytest.fixture
def report(formatters, dto_storage):
    return Report(formatters=formatters, dto_storage=dto_storage)


class TestReport:
    def test_initialization_with_formatters_and_storages(
        self, formatters, dto_storage
    ):
        report = Report(
            formatters=formatters, dto_storage=dto_storage
        )

        assert len(report.formatters) == 3
        assert report.dto_storage == dto_storage
        assert len(report.formatters_by_type_artifact_and_format) == 3

    def test_initialization_with_duplicate_formatter(
        self, dto_storage
    ):
        duplicate_formatters = [
            TxtTestCaseReportFormatter(),
            TxtTestCaseReportFormatter(),
        ]

        with pytest.raises(
            ReportError, match="Formatter.*already registered"
        ):
            Report(formatters=duplicate_formatters, dto_storage=dto_storage)  # type: ignore

    def test_create_report_from_testcase_result(
        self, report, testcase_result
    ):
        report_dto = report.create_report(testcase_result)

        assert isinstance(report_dto, TestCaseReportDTO)
        assert (
            report_dto.testcase_id == testcase_result.testcase_id
        )
        assert report_dto.testrun_id == testcase_result.testrun_id
        assert (
            report_dto.testobject == testcase_result.testobject.name
        )
        assert (
            report_dto.testtype == testcase_result.testtype.value
        )
        assert report_dto.diff == testcase_result.diff
        assert report_dto.summary == testcase_result.summary
        assert report_dto.facts == testcase_result.facts
        assert report_dto.details == testcase_result.details
        assert (
            report_dto.specifications
            == testcase_result.specifications
        )
        assert report_dto.result == testcase_result.result.value
        assert report_dto.start_ts == testcase_result.start_ts
        assert report_dto.end_ts == testcase_result.end_ts

    def test_create_report_from_testrun_result(
        self, report, testrun
    ):
        report_dto = report.create_report(testrun)

        assert isinstance(report_dto, TestRunReportDTO)
        assert report_dto.testrun_id == testrun.testrun_id
        assert report_dto.result == testrun.result.value
        assert report_dto.start_ts == testrun.start_ts
        assert report_dto.end_ts == testrun.end_ts
        assert len(report_dto.testcase_results) == len(
            testrun.testcase_results
        )

        for i, testcase_result in enumerate(
            testrun.testcase_results
        ):
            dto_testcase = report_dto.testcase_results[i]
            assert (
                dto_testcase.testrun_id
                == testcase_result.testrun_id
            )
            assert (
                dto_testcase.testobject
                == testcase_result.testobject.name
            )
            assert (
                dto_testcase.testtype
                == testcase_result.testtype.value
            )
            assert (
                dto_testcase.summary == testcase_result.summary
            )
            assert (
                dto_testcase.result
                == testcase_result.result.value
            )
            assert (
                dto_testcase.start_ts == testcase_result.start_ts
            )
            assert dto_testcase.end_ts == testcase_result.end_ts

    def test_create_report_with_wrong_type(self, report):
        invalid_result = Mock()

        with pytest.raises(
            WrongReportTypeError, match="Wrong report type"
        ):
            report.create_report(invalid_result)

    def test_save_and_retrieve_report(
        self, report, testcase_report, testrun_report
    ):
        report.save_report(testcase_report)
        report.save_report(testrun_report)

        retrieved_testcase_report = report.retrieve_report(
            report_id=str(testcase_report.report_id),
            report_type=ReportType.TESTCASE,
        )
        retrieved_testrun_report = report.retrieve_report(
            report_id=str(testrun_report.report_id),
            report_type=ReportType.TESTRUN,
        )

        assert isinstance(
            retrieved_testcase_report, TestCaseReportDTO
        )
        assert (
            retrieved_testcase_report.testcase_id
            == testcase_report.testcase_id
        )
        assert (
            retrieved_testcase_report.testrun_id
            == testcase_report.testrun_id
        )
        assert (
            retrieved_testrun_report.testrun_id
            == testrun_report.testrun_id
        )
        assert (
            retrieved_testrun_report.result
            == testrun_report.result
        )
        assert (
            retrieved_testrun_report.start_ts
            == testrun_report.start_ts
        )
        assert (
            retrieved_testrun_report.end_ts
            == testrun_report.end_ts
        )
        assert len(
            retrieved_testrun_report.testcase_results
        ) == len(testrun_report.testcase_results)

    def test_create_artifact_for_testcase_report(
        self, report, testcase_report
    ):
        artifact_bytes = report.create_artifact(
            report=testcase_report,
            artifact=ReportArtifact.DIFF,
            artifact_format=ReportArtifactFormat.XLSX,
        )
        assert isinstance(artifact_bytes, bytes)
        assert artifact_bytes.startswith(b"PK\x03\x04")

        artifact_bytes = report.create_artifact(
            report=testcase_report,
            artifact=ReportArtifact.REPORT,
            artifact_format=ReportArtifactFormat.TXT,
        )
        artifact_txt = artifact_bytes.decode()
        assert isinstance(artifact_bytes, bytes)
        assert testcase_report.summary in artifact_txt

    def test_create_artifact_for_testrun_report(
        self, report, testrun_report
    ):
        artifact_bytes = report.create_artifact(
            report=testrun_report,
            artifact=ReportArtifact.REPORT,
            artifact_format=ReportArtifactFormat.XLSX,
        )
        assert isinstance(artifact_bytes, bytes)
        assert artifact_bytes.startswith(b"PK\x03\x04")

    def test_create_artifact_without_artifact_for_testcase(
        self, report, testcase_report
    ):
        with pytest.raises(
            ReportArtifactNotSpecifiedError,
            match="Artifact.*must be specified",
        ):
            report.create_artifact(
                report=testcase_report,
                artifact_format=ReportArtifactFormat.JSON,
            )

    def test_create_artifact_with_wrong_report_type(
        self, report
    ):
        invalid_report = Mock()

        with pytest.raises(
            WrongReportTypeError, match="Wrong report type"
        ):
            report.create_artifact(
                report=invalid_report,
                artifact_format=ReportArtifactFormat.JSON,
            )

    def test_create_artifact_with_no_formatter_found(
        self, report, testcase_report
    ):
        with pytest.raises(
            NoFormatterFoundError,
            match="Formatter for.*not registered",
        ):
            report.create_artifact(
                report=testcase_report,
                artifact_format=ReportArtifactFormat.JSON,
                artifact=ReportArtifact.DIFF,
            )
