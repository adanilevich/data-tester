import json
import pytest
from datetime import datetime
from uuid import uuid4

import polars as pl

from src.config import Config
from src.dtos import (
    TestCaseReportDTO,
    TestRunReportDTO,
    ReportArtifact,
    ReportArtifactFormat,
    TestResult,
    TestType,
)
from src.storage.dict_storage import DictStorage
from src.report.application.handle_reports import (
    ReportCommandHandler,
    InvalidReportTypeError,
)
from src.report.ports.drivers import (
    CreateReportCommand,
    SaveReportCommand,
    GetTestCaseReportArtifactCommand,
    GetTestrunReportArtifactCommand,
    SaveReportArtifactsForUsersCommand,
)
from src.report.ports.infrastructure import ObjectNotFoundError
from src.report.adapters.plugins import (
    JsonTestCaseReportFormatter,
    JsonTestRunReportFormatter,
    TxtTestCaseReportFormatter,
    XlsxTestCaseDiffFormatter,
    XlsxTestRunReportFormatter,
)


@pytest.fixture
def config() -> Config:
    """Create a test config with INTERNAL_TESTREPORT_LOCATION set"""
    config = Config(INTERNAL_TESTREPORT_LOCATION="dict:///test_reports")

    return config


@pytest.fixture
def formatters():
    """Create all available formatters"""
    return [
        JsonTestCaseReportFormatter(),
        JsonTestRunReportFormatter(),
        TxtTestCaseReportFormatter(),
        XlsxTestCaseDiffFormatter(),
        XlsxTestRunReportFormatter(),
    ]


@pytest.fixture
def report_handler(config, formatters) -> ReportCommandHandler:
    """Create a ReportCommandHandler with real formatters and storage"""
    handler = ReportCommandHandler(
        config=config, formatters=formatters, storages=[DictStorage()]
    )
    return handler


class TestReportCommandHandler:
    """Test suite for ReportCommandHandler"""

    def test_create_testcase_report(self, report_handler, testcase_result):
        """Test creating a report from a test case result"""
        command = CreateReportCommand(result=testcase_result)

        result = report_handler.create_report(command)

        assert isinstance(result, TestCaseReportDTO)
        assert result.testcase_id == testcase_result.testcase_id
        assert result.testrun_id == testcase_result.testrun_id
        assert result.result == testcase_result.result.value
        assert result.testobject == testcase_result.testobject.name
        assert result.testtype == testcase_result.testtype.value

    def test_create_testrun_report(self, report_handler, testrun_result):
        """Test creating a report from a test run result"""
        command = CreateReportCommand(result=testrun_result)

        result = report_handler.create_report(command)

        assert isinstance(result, TestRunReportDTO)
        assert result.testrun_id == testrun_result.testrun_id
        assert result.result == testrun_result.result.value
        assert len(result.testcase_results) == len(testrun_result.testcase_results)

    def test_save_testcase_report(self, report_handler, testcase_report):
        """Test saving a test case report"""
        location = "dict:///test_reports"
        command = SaveReportCommand(report=testcase_report, location=location)
        storage = report_handler.storages[0]

        report_handler.save_report(command)

        # Verify the report was saved
        expected_path = (
            f"{location}/testcase_reports/{testcase_report.testrun_id}" +
            f"_{testcase_report.testcase_id}.json"
        )
        saved_content = storage.read(expected_path)

        # Should be valid JSON
        parsed_report = json.loads(saved_content.decode("utf-8"))
        assert parsed_report["testcase_id"] == str(testcase_report.testcase_id)
        assert parsed_report["testrun_id"] == str(testcase_report.testrun_id)

    def test_save_testrun_report(self, report_handler, testrun_report):
        """Test saving a test run report"""
        location = "dict:///test_reports"
        command = SaveReportCommand(report=testrun_report, location=location)
        storage = report_handler.storages[0]

        report_handler.save_report(command)

        # Verify the report was saved
        expected_path = f"{location}/testrun_reports/{testrun_report.testrun_id}.json"
        saved_content = storage.read(expected_path)

        # Should be valid JSON
        parsed_report = json.loads(saved_content.decode("utf-8"))
        assert parsed_report["testrun_id"] == str(testrun_report.testrun_id)

    def test_save_report_invalid_type(self, report_handler, testcase_report):
        """Test saving an invalid report type raises error"""
        # Create a mock object that looks like a report but isn't a valid DTO
        mock_report = type("MockReport", (), {"testrun_id": uuid4()})()

        # We need to bypass the validation by creating the command directly
        # since Pydantic would reject the invalid type
        location = "dict:///test_reports"
        command = SaveReportCommand(report=testcase_report, location=location)
        # Then replace the report with our invalid one
        command.report = mock_report

        with pytest.raises(InvalidReportTypeError):
            report_handler.save_report(command)

    def test_get_testcase_artifact(self, report_handler, testcase_report):
        """Test retrieving a test case report artifact"""
        # First save the report
        location = "dict:///test_reports"
        save_command = SaveReportCommand(report=testcase_report, location=location)
        report_handler.save_report(save_command)

        # Then retrieve it
        get_command = GetTestCaseReportArtifactCommand(
            testrun_id=str(testcase_report.testrun_id),
            testcase_id=str(testcase_report.testcase_id),
            location=location,
            artifact=ReportArtifact.REPORT,
            artifact_format=ReportArtifactFormat.TXT,
        )

        result = report_handler.get_testcase_report_artifact(get_command)

        assert isinstance(result, bytes)
        text_content = result.decode("utf-8")
        assert testcase_report.summary in text_content

    def test_get_testcase_artifact_wrong_id(self, report_handler, testrun_report):
        """Test retrieving test case artifact from test run report raises error"""
        # Save a test run report
        location = "dict:///test_reports"
        save_command = SaveReportCommand(report=testrun_report, location=location)
        report_handler.save_report(save_command)

        # Try to get testcase artifact using a testcase_id that doesn't exist
        get_command = GetTestCaseReportArtifactCommand(
            testrun_id=str(testrun_report.testrun_id),
            testcase_id="non_existent_testcase_id",
            location=location,
            artifact=ReportArtifact.REPORT,
            artifact_format=ReportArtifactFormat.TXT,
        )

        # This should fail because the path doesn't exist
        with pytest.raises(ObjectNotFoundError):
            report_handler.get_testcase_report_artifact(get_command)

    def test_get_testrun_artifact(self, report_handler, testrun_report):
        """Test retrieving a test run report artifact"""
        # First save the report
        location = "dict:///test_reports"
        save_command = SaveReportCommand(report=testrun_report, location=location)
        report_handler.save_report(save_command)

        # Then retrieve it
        command = GetTestrunReportArtifactCommand(
            testrun_id=str(testrun_report.testrun_id),
            location=location,
            artifact_format=ReportArtifactFormat.XLSX,
        )

        result = report_handler.get_testrun_report_artifact(command)

        assert isinstance(result, bytes)
        report = pl.read_excel(result)
        expected_columns = list(testrun_report.testcase_results[0].to_dict().keys())
        assert report.columns == expected_columns

        expected_rowcount = len(testrun_report.testcase_results)
        assert report.shape[0] == expected_rowcount

    def test_save_for_users_testcase(self, report_handler, testcase_report):
        """Test saving user artifacts for test case report"""
        report = testcase_report
        report.diff = {"any_diff": {"a": [1, 2, 3], "b": [4, 5, 6]}}
        report.testtype = TestType.SCHEMA.value
        report.result = TestResult.NOK.value
        location = "dict:///user_reports"
        storage = report_handler.storages[0]

        command = SaveReportArtifactsForUsersCommand(report=report, location=location)
        report_handler.save_report_artifacts_for_users(command)

        # Should save report artifact
        date_str = datetime.now().strftime("%Y-%m-%d")
        expected_report_path = (
            f"dict:///user_reports/{date_str}/{report.testrun_id}/" +
            f"{report.testobject}_{report.testtype}_report.txt"
        )
        report_content = storage.read(expected_report_path)
        assert isinstance(report_content, bytes)

        # Should save diff artifact since testcase has diff
        expected_diff_path = (
            f"dict:///user_reports/{date_str}/{report.testrun_id}/" +
            f"{report.testobject}_{report.testtype}_diff.xlsx"
        )
        diff_content = storage.read(expected_diff_path)

        # diff artifact should contain all columns and rows
        diff_df = pl.read_excel(diff_content)
        assert diff_df.columns == list(report.diff["any_diff"].keys())
        assert diff_df.shape[0] == len(report.diff["any_diff"]["a"])

    def test_save_for_users_testcase_no_diff(self, report_handler, testcase_report):
        """Test saving user artifacts for test case report without diff"""
        # Create test case report without diff
        report = testcase_report
        report.diff = {}
        report.testtype = TestType.SCHEMA.value
        report.result = TestResult.OK.value
        location = "dict:///user_reports"
        storage = report_handler.storages[0]

        command = SaveReportArtifactsForUsersCommand(report=report, location=location)
        report_handler.save_report_artifacts_for_users(command)

        # Should save report artifact
        date_str = datetime.now().strftime("%Y-%m-%d")
        expected_report_path = (
            f"{location}/{date_str}/{report.testrun_id}/" +
            f"{report.testobject}_{report.testtype}_report.txt"
        )
        report_content = storage.read(expected_report_path)
        assert isinstance(report_content, bytes)

        # Should NOT save diff artifact since no diff
        expected_diff_path = (
            f"{location}/{date_str}/{report.testrun_id}/" +
            f"{report.testobject}_{report.testtype}_diff.xlsx"
        )
        with pytest.raises(ObjectNotFoundError):
            storage.read(expected_diff_path)

    def test_save_for_users_testrun(self, report_handler, testrun_report):
        """Test saving user artifacts for test run report"""
        # Given a saved testrun report
        location = "dict:///user_reports"
        command = SaveReportArtifactsForUsersCommand(report=testrun_report, location=location)
        report_handler.save_report_artifacts_for_users(command)
        storage = report_handler.storages[0]

        # Should save report artifact
        date_str = datetime.now().strftime("%Y-%m-%d")
        datetime_str = testrun_report.start_ts.strftime('%Y-%m-%d_%H-%M-%S')
        expected_report_path = (
            f"{location}/{date_str}/{testrun_report.testrun_id}/" +
            f"testrun_report_{datetime_str}.xlsx"
        )

        report_content = storage.read(expected_report_path)
        assert isinstance(report_content, bytes)
        assert report_content.startswith(b"PK\x03\x04")  # XLSX format
