import pytest

from src.domain.report import (
    Report,
    NoFormatterFoundError,
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
    def test_initialization_with_formatters_and_storages(self, formatters, dto_storage):
        report = Report(formatters=formatters, dto_storage=dto_storage)

        assert len(report.formatters) == 3
        assert report.dto_storage == dto_storage
        assert len(report.formatters_by_type_artifact_and_format) == 3

    def test_initialization_with_duplicate_formatter(self, dto_storage):
        duplicate_formatters = [
            TxtTestCaseReportFormatter(),
            TxtTestCaseReportFormatter(),
        ]

        with pytest.raises(ReportError, match="Formatter.*already registered"):
            Report(formatters=duplicate_formatters, dto_storage=dto_storage)  # type: ignore

    def test_create_testcase_report(self, report, testcase_result):
        report_dto = report.create_testcase_report(testcase_result)

        assert isinstance(report_dto, TestCaseReportDTO)
        assert report_dto.testcase_id == testcase_result.id
        assert report_dto.testrun_id == testcase_result.testrun_id
        assert report_dto.testobject == testcase_result.testobject.name
        assert report_dto.testtype == testcase_result.testtype.value
        assert report_dto.diff == testcase_result.diff
        assert report_dto.summary == testcase_result.summary
        assert report_dto.facts == testcase_result.facts
        assert report_dto.details == testcase_result.details
        assert report_dto.specs == testcase_result.specs
        assert report_dto.result == testcase_result.result.value
        assert report_dto.start_ts == testcase_result.start_ts
        assert report_dto.end_ts == testcase_result.end_ts

    def test_create_testrun_report(self, report, testrun):
        report_dto = report.create_testrun_report(testrun)

        assert isinstance(report_dto, TestRunReportDTO)
        assert report_dto.testrun_id == testrun.id
        assert report_dto.result == testrun.result.value
        assert report_dto.start_ts == testrun.start_ts
        assert report_dto.end_ts == testrun.end_ts
        assert len(report_dto.testcase_results) == len(testrun.results)

        for i, testcase_result in enumerate(testrun.results):
            dto_testcase = report_dto.testcase_results[i]
            assert dto_testcase.testrun_id == testcase_result.testrun_id
            assert dto_testcase.testobject == testcase_result.testobject.name
            assert dto_testcase.testtype == testcase_result.testtype.value
            assert dto_testcase.summary == testcase_result.summary
            assert dto_testcase.result == testcase_result.result.value
            assert dto_testcase.start_ts == testcase_result.start_ts
            assert dto_testcase.end_ts == testcase_result.end_ts

    def test_save_and_load_testcase_report(self, report, testcase_report):
        report.save_report(testcase_report)

        loaded = report.load_testcase_report(report_id=str(testcase_report.report_id))

        assert isinstance(loaded, TestCaseReportDTO)
        assert loaded.testcase_id == testcase_report.testcase_id
        assert loaded.testrun_id == testcase_report.testrun_id

    def test_save_and_load_testrun_report(self, report, testrun_report):
        report.save_report(testrun_report)

        loaded = report.load_testrun_report(report_id=str(testrun_report.report_id))

        assert isinstance(loaded, TestRunReportDTO)
        assert loaded.testrun_id == testrun_report.testrun_id
        assert loaded.result == testrun_report.result
        assert loaded.start_ts == testrun_report.start_ts
        assert loaded.end_ts == testrun_report.end_ts
        assert len(loaded.testcase_results) == len(testrun_report.testcase_results)

    def test_create_testcase_report_artifact(self, report, testcase_report):
        artifact_bytes = report.create_testcase_report_artifact(
            report=testcase_report,
            artifact=ReportArtifact.DIFF,
            artifact_format=ReportArtifactFormat.XLSX,
        )
        assert isinstance(artifact_bytes, bytes)
        assert artifact_bytes.startswith(b"PK\x03\x04")

        artifact_bytes = report.create_testcase_report_artifact(
            report=testcase_report,
            artifact=ReportArtifact.REPORT,
            artifact_format=ReportArtifactFormat.TXT,
        )
        artifact_txt = artifact_bytes.decode()
        assert isinstance(artifact_bytes, bytes)
        assert testcase_report.summary in artifact_txt

    def test_create_testrun_report_artifact(self, report, testrun_report):
        artifact_bytes = report.create_testrun_report_artifact(
            report=testrun_report,
            artifact_format=ReportArtifactFormat.XLSX,
        )
        assert isinstance(artifact_bytes, bytes)
        assert artifact_bytes.startswith(b"PK\x03\x04")

    def test_create_testcase_report_artifact_no_formatter(self, report, testcase_report):
        with pytest.raises(NoFormatterFoundError, match="Formatter for.*not registered"):
            report.create_testcase_report_artifact(
                report=testcase_report,
                artifact=ReportArtifact.DIFF,
                artifact_format=ReportArtifactFormat.JSON,
            )

    def test_list_testcase_reports(self, report, testcase_report):
        report.save_report(testcase_report)

        results = report.list_testcase_reports(domain=testcase_report.domain)
        assert len(results) == 1
        assert results[0].testcase_id == testcase_report.testcase_id

    def test_list_testrun_reports(self, report, testrun_report):
        report.save_report(testrun_report)

        results = report.list_testrun_reports(domain=testrun_report.domain)
        assert len(results) == 1
        assert results[0].testrun_id == testrun_report.testrun_id

    def test_create_and_save_all_reports(self, report, testrun):
        result = report.create_and_save_all_reports(testrun)

        # testrun report was created and saved
        assert isinstance(result, TestRunReportDTO)
        loaded_testrun_report = report.load_testrun_report(
            report_id=str(result.report_id)
        )
        assert loaded_testrun_report.testrun_id == testrun.id

        # testcase reports were created and saved
        testcase_reports = report.list_testcase_reports(domain=testrun.domain)
        assert len(testcase_reports) == len(testrun.results)

        # report_ids were set on testrun and testcases
        assert testrun.report_id == result.report_id
        for tc in testrun.results:
            assert tc.report_id is not None
