import uuid
import pytest
from uuid import uuid4

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
from src.domain import ReportCommandHandler
from src.domain.report.handle_reports import InvalidReportTypeError
from src.domain_ports import (
    CreateReportCommand,
    SaveReportCommand,
    GetReportArtifactCommand,
    LoadReportCommand,
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
def report_handler(
    formatters, dto_storage
) -> ReportCommandHandler:
    return ReportCommandHandler(
        formatters=formatters, dto_storage=dto_storage
    )


class TestReportCommandHandler:
    """Test suite for ReportCommandHandler"""

    def test_create_testcase_report(
        self, report_handler, testcase_result
    ):
        """Test creating a report from a test case result"""
        command = CreateReportCommand(result=testcase_result)

        result = report_handler.create_report(command)

        assert isinstance(result, TestCaseReportDTO)
        assert result.testcase_id == testcase_result.testcase_id
        assert result.testrun_id == testcase_result.testrun_id
        assert result.result == testcase_result.result.value
        assert (
            result.testobject == testcase_result.testobject.name
        )
        assert result.testtype == testcase_result.testtype.value

    def test_create_testrun_report(
        self, report_handler, testrun
    ):
        """Test creating a report from a test run result"""
        command = CreateReportCommand(result=testrun)

        result = report_handler.create_report(command)

        assert isinstance(result, TestRunReportDTO)
        assert result.testrun_id == testrun.testrun_id
        assert result.result == testrun.result.value
        assert len(result.testcase_results) == len(
            testrun.testcase_results
        )

    def test_save_load_roundtrip_testcase_report(
        self, report_handler, testcase_report
    ):
        """Test saving and loading a test case report"""
        command = SaveReportCommand(report=testcase_report)

        report_handler.save_report(command)

        load_command = LoadReportCommand(
            report_id=testcase_report.report_id,
            report_type=ReportType.TESTCASE,
        )
        loaded_report = report_handler.load_report(load_command)

        assert loaded_report == testcase_report

    def test_save_load_roundtrip_testrun_report(
        self, report_handler, testrun_report
    ):
        """Test saving and loading a test run report"""
        command = SaveReportCommand(report=testrun_report)

        report_handler.save_report(command)

        load_command = LoadReportCommand(
            report_id=testrun_report.report_id,
            report_type=ReportType.TESTRUN,
        )
        loaded_report = report_handler.load_report(load_command)

        assert loaded_report == testrun_report

    def test_save_report_invalid_type(
        self, report_handler, testcase_report
    ):
        """Test saving an invalid report type raises error"""
        mock_report = type(
            "MockReport", (), {"testrun_id": uuid4()}
        )()

        command = SaveReportCommand(report=testcase_report)
        command.report = mock_report  # type: ignore

        with pytest.raises(InvalidReportTypeError):
            report_handler.save_report(command)

    def test_get_testcase_artifact(
        self, report_handler, testcase_report
    ):
        """Test retrieving a test case report artifact"""
        save_command = SaveReportCommand(
            report=testcase_report
        )
        report_handler.save_report(save_command)

        get_command = GetReportArtifactCommand(
            report_id=testcase_report.report_id,
            report_type=ReportType.TESTCASE,
            artifact=ReportArtifact.REPORT,
            artifact_format=ReportArtifactFormat.TXT,
        )

        result = report_handler.get_report_artifact(get_command)

        assert isinstance(result, bytes)
        text_content = result.decode("utf-8")
        assert testcase_report.summary in text_content

    def test_get_testcase_artifact_wrong_id(
        self, report_handler, testrun_report
    ):
        """Test retrieving artifact for non-existent id raises error"""
        save_command = SaveReportCommand(
            report=testrun_report
        )
        report_handler.save_report(save_command)

        get_command = GetReportArtifactCommand(
            report_id=uuid.uuid4(),
            report_type=ReportType.TESTCASE,
            artifact=ReportArtifact.REPORT,
            artifact_format=ReportArtifactFormat.TXT,
        )

        with pytest.raises(ObjectNotFoundError):
            report_handler.get_report_artifact(get_command)

    def test_get_testrun_artifact(
        self, report_handler, testrun_report
    ):
        """Test retrieving a test run report artifact"""
        save_command = SaveReportCommand(
            report=testrun_report
        )
        report_handler.save_report(save_command)

        command = GetReportArtifactCommand(
            report_id=testrun_report.report_id,
            report_type=ReportType.TESTRUN,
            artifact=ReportArtifact.REPORT,
            artifact_format=ReportArtifactFormat.XLSX,
        )

        result = report_handler.get_report_artifact(command)
        assert isinstance(result, bytes)
        assert result.startswith(b"PK\x03\x04")  # XLSX format
