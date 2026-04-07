import uuid
import pytest
from uuid import uuid4

from src.dtos import (
    TestCaseReportDTO,
    TestRunReportDTO,
    ReportArtifact,
    ReportArtifactFormat,
)
from src.infrastructure.storage.dto_storage_file import MemoryDtoStorage
from src.infrastructure.storage.dto_storage_file import JsonSerializer
from src.dtos import LocationDTO
from src.domain_adapters import ReportAdapter, InvalidReportTypeError
from src.domain_ports import (
    CreateTestCaseReportCommand,
    CreateTestRunReportCommand,
    SaveReportCommand,
    CreateTestCaseReportArtifactCommand,
    CreateTestRunReportArtifactCommand,
    LoadTestCaseReportCommand,
    LoadTestRunReportCommand,
    ListTestCaseReportsCommand,
    ListTestRunReportsCommand,
    CreateAndSaveAllReportsCommand,
)
from src.infrastructure.storage import ObjectNotFoundError
from src.domain.report.plugins import (
    TxtTestCaseReportFormatter,
    XlsxTestCaseDiffFormatter,
    XlsxTestRunReportFormatter,
)


@pytest.fixture
def formatters():
    """Create all available formatters"""
    return [
        TxtTestCaseReportFormatter(),
        XlsxTestCaseDiffFormatter(),
        XlsxTestRunReportFormatter(),
    ]


@pytest.fixture
def dto_storage() -> MemoryDtoStorage:
    return MemoryDtoStorage(
        serializer=JsonSerializer(),
        storage_location=LocationDTO("memory://test/"),
    )


@pytest.fixture
def report_handler(formatters, dto_storage) -> ReportAdapter:
    return ReportAdapter(formatters=formatters, dto_storage=dto_storage)


class TestReportAdapter:
    """Test suite for ReportAdapter"""

    def test_create_testcase_report(self, report_handler, testcase_result):
        """Test creating a report from a test case result"""
        command = CreateTestCaseReportCommand(result=testcase_result)

        result = report_handler.create_testcase_report(command)

        assert isinstance(result, TestCaseReportDTO)
        assert result.testcase_id == testcase_result.id
        assert result.testrun_id == testcase_result.testrun_id  # testrun_id stays
        assert result.result == testcase_result.result.value
        assert result.testobject == testcase_result.testobject.name
        assert result.testtype == testcase_result.testtype.value

    def test_create_testrun_report(self, report_handler, testrun):
        """Test creating a report from a test run result"""
        command = CreateTestRunReportCommand(result=testrun)

        result = report_handler.create_testrun_report(command)

        assert isinstance(result, TestRunReportDTO)
        assert result.testrun_id == testrun.id
        assert result.result == testrun.result.value
        assert len(result.testcase_results) == len(testrun.results)

    def test_save_load_roundtrip_testcase_report(self, report_handler, testcase_report):
        """Test saving and loading a test case report"""
        save_command = SaveReportCommand(report=testcase_report)
        report_handler.save_report(save_command)

        load_command = LoadTestCaseReportCommand(
            report_id=testcase_report.report_id,
        )
        loaded_report = report_handler.load_testcase_report(load_command)

        assert loaded_report == testcase_report

    def test_save_load_roundtrip_testrun_report(self, report_handler, testrun_report):
        """Test saving and loading a test run report"""
        save_command = SaveReportCommand(report=testrun_report)
        report_handler.save_report(save_command)

        load_command = LoadTestRunReportCommand(
            report_id=testrun_report.report_id,
        )
        loaded_report = report_handler.load_testrun_report(load_command)

        assert loaded_report == testrun_report

    def test_save_report_invalid_type(self, report_handler, testcase_report):
        """Test saving an invalid report type raises error"""
        mock_report = type("MockReport", (), {"testrun_id": uuid4()})()

        command = SaveReportCommand(report=testcase_report)
        command.report = mock_report  # type: ignore

        with pytest.raises(InvalidReportTypeError):
            report_handler.save_report(command)

    def test_create_testcase_report_artifact(self, report_handler, testcase_report):
        """Test retrieving a test case report artifact"""
        save_command = SaveReportCommand(report=testcase_report)
        report_handler.save_report(save_command)

        get_command = CreateTestCaseReportArtifactCommand(
            report_id=testcase_report.report_id,
            artifact=ReportArtifact.REPORT,
            artifact_format=ReportArtifactFormat.TXT,
        )

        result = report_handler.create_testcase_report_artifact(get_command)

        assert isinstance(result, bytes)
        text_content = result.decode("utf-8")
        assert testcase_report.summary in text_content

    def test_create_testcase_report_artifact_wrong_id(
        self, report_handler, testrun_report
    ):
        """Test retrieving artifact for non-existent id raises error"""
        save_command = SaveReportCommand(report=testrun_report)
        report_handler.save_report(save_command)

        get_command = CreateTestCaseReportArtifactCommand(
            report_id=uuid.uuid4(),
            artifact=ReportArtifact.REPORT,
            artifact_format=ReportArtifactFormat.TXT,
        )

        with pytest.raises(ObjectNotFoundError):
            report_handler.create_testcase_report_artifact(get_command)

    def test_create_testrun_report_artifact(self, report_handler, testrun_report):
        """Test retrieving a test run report artifact"""
        save_command = SaveReportCommand(report=testrun_report)
        report_handler.save_report(save_command)

        command = CreateTestRunReportArtifactCommand(
            report_id=testrun_report.report_id,
            artifact_format=ReportArtifactFormat.XLSX,
        )

        result = report_handler.create_testrun_report_artifact(command)
        assert isinstance(result, bytes)
        assert result.startswith(b"PK\x03\x04")  # XLSX format

    def test_list_testcase_reports(self, report_handler, testcase_report):
        """Test listing testcase reports by domain"""
        save_command = SaveReportCommand(report=testcase_report)
        report_handler.save_report(save_command)

        list_command = ListTestCaseReportsCommand(domain=testcase_report.domain)
        results = report_handler.list_testcase_reports(list_command)

        assert len(results) == 1
        assert results[0].testcase_id == testcase_report.testcase_id

    def test_list_testrun_reports(self, report_handler, testrun_report):
        """Test listing testrun reports by domain"""
        save_command = SaveReportCommand(report=testrun_report)
        report_handler.save_report(save_command)

        list_command = ListTestRunReportsCommand(domain=testrun_report.domain)
        results = report_handler.list_testrun_reports(list_command)

        assert len(results) == 1
        assert results[0].testrun_id == testrun_report.testrun_id

    def test_create_and_save_all_reports(self, report_handler, testrun):
        """Test creating and saving all reports for a testrun"""
        command = CreateAndSaveAllReportsCommand(testrun=testrun)
        result = report_handler.create_and_save_all_reports(command)

        assert isinstance(result, TestRunReportDTO)
        assert testrun.report_id == result.report_id
        for tc in testrun.results:
            assert tc.report_id is not None
