import json
import pytest
from datetime import datetime
from uuid import uuid4

import polars as pl

from src.dtos import (
    TestCaseReportDTO,
    TestRunReportDTO,
    ReportArtifact,
    ReportArtifactFormat,
    TestResult,
    TestType,
    LocationDTO,
)
from src.storage.dict_storage import DictStorage
from src.report.application.handle_reports import (
    ReportCommandHandler,
    InvalidReportTypeError,
)
from src.report.ports.drivers import (
    CreateReportCommand,
    SaveReportCommand,
    GetReportArtifactCommand,
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
def report_handler(formatters) -> ReportCommandHandler:
    """Create a ReportCommandHandler with real formatters and storage"""
    handler = ReportCommandHandler(formatters=formatters, storages=[DictStorage()])
    return handler


class TestReportCommandHandler:
    """Test suite for ReportCommandHandler"""

    def test_create_testcase_report(self, report_handler, testcase_result):
        """Test creating a report from a test case result"""
        # Given: a test case result and a report handler
        command = CreateReportCommand(result=testcase_result)

        # When: creating a report from the test case result
        result = report_handler.create_report(command)

        # Then: the result should be a TestCaseReportDTO with correct data
        assert isinstance(result, TestCaseReportDTO)
        assert result.testcase_id == testcase_result.testcase_id
        assert result.testrun_id == testcase_result.testrun_id
        assert result.result == testcase_result.result.value
        assert result.testobject == testcase_result.testobject.name
        assert result.testtype == testcase_result.testtype.value

    def test_create_testrun_report(self, report_handler, testrun_result):
        """Test creating a report from a test run result"""
        # Given: a test run result and a report handler
        command = CreateReportCommand(result=testrun_result)

        # When: creating a report from the test run result
        result = report_handler.create_report(command)

        # Then: the result should be a TestRunReportDTO with correct data
        assert isinstance(result, TestRunReportDTO)
        assert result.testrun_id == testrun_result.testrun_id
        assert result.result == testrun_result.result.value
        assert len(result.testcase_results) == len(testrun_result.testcase_results)

    def test_save_testcase_report(self, report_handler, testcase_report):
        """Test saving a test case report"""
        # Given: a test case report, storage location, and report handler
        location = LocationDTO("dict://test_reports")
        command = SaveReportCommand(
            report=testcase_report,
            location=location,
            artifact_format=ReportArtifactFormat.JSON
        )
        storage = report_handler.storages[0]

        # When: saving the test case report
        report_handler.save_report(command)

        # Then: the report should be saved to the expected location with correct content
        expected_path = location.append(f"{testcase_report.report_id}.json")
        saved_content = storage.read(expected_path)

        # Should be valid JSON
        parsed_report = json.loads(saved_content.decode("utf-8"))
        assert parsed_report["testcase_id"] == str(testcase_report.testcase_id)
        assert parsed_report["testrun_id"] == str(testcase_report.testrun_id)

    def test_save_testrun_report(self, report_handler, testrun_report):
        """Test saving a test run report"""
        # Given: a test run report, storage location, and report handler
        location = LocationDTO("dict://test_reports")
        command = SaveReportCommand(
            report=testrun_report,
            location=location,
            artifact_format=ReportArtifactFormat.JSON
        )
        storage = report_handler.storages[0]

        # When: saving the test run report
        report_handler.save_report(command)

        # Then: the report should be saved to the expected location with correct content
        expected_path = location.append(f"{testrun_report.report_id}.json")
        saved_content = storage.read(expected_path)

        # Should be valid JSON
        parsed_report = json.loads(saved_content.decode("utf-8"))
        assert parsed_report["testrun_id"] == str(testrun_report.testrun_id)

    def test_save_report_invalid_type(self, report_handler, testcase_report):
        """Test saving an invalid report type raises error"""
        # Given: a mock object that looks like a report but isn't a valid DTO
        mock_report = type("MockReport", (), {"testrun_id": uuid4()})()

        # We need to bypass the validation by creating the command directly
        # since Pydantic would reject the invalid type
        location = LocationDTO("dict://test_reports")
        command = SaveReportCommand(
            report=testcase_report,
            location=location,
            artifact_format=ReportArtifactFormat.JSON
        )
        # ... and then replace the report with our invalid one
        command.report = mock_report

        # When: trying to save an invalid report type
        # Then: an InvalidReportTypeError should be raised
        with pytest.raises(InvalidReportTypeError):
            report_handler.save_report(command)

    def test_get_testcase_artifact(self, report_handler, testcase_report):
        """Test retrieving a test case report artifact"""
        # Given: a saved test case report and a report handler
        location = LocationDTO("dict://test_reports")
        save_command = SaveReportCommand(
            report=testcase_report,
            location=location,
            artifact_format=ReportArtifactFormat.JSON
        )
        report_handler.save_report(save_command)

        # When: retrieving a test case artifact in TXT format
        get_command = GetReportArtifactCommand(
            report_id=testcase_report.report_id,
            location=location,
            internal_artifact_format=ReportArtifactFormat.JSON,
            artifact=ReportArtifact.REPORT,
            artifact_format=ReportArtifactFormat.TXT,
        )

        result = report_handler.get_report_artifact(get_command)

        # Then: the result should be bytes containing the test case summary
        assert isinstance(result, bytes)
        text_content = result.decode("utf-8")
        assert testcase_report.summary in text_content

    def test_get_testcase_artifact_wrong_id(self, report_handler, testrun_report):
        """Test retrieving test case artifact from test run report raises error"""
        # Given: a saved test run report
        location = LocationDTO("dict://test_reports")
        save_command = SaveReportCommand(
            report=testrun_report,
            location=location,
            artifact_format=ReportArtifactFormat.JSON
        )
        report_handler.save_report(save_command)

        # When: trying to get testcase artifact using a testcase_id that doesn't exist
        get_command = GetReportArtifactCommand(
            report_id=testrun_report.report_id,
            location=location,
            internal_artifact_format=ReportArtifactFormat.JSON,
            artifact=ReportArtifact.REPORT,
            artifact_format=ReportArtifactFormat.TXT,
        )

        # Then: an InvalidReportTypeError should be raised because we can't create
        # testcase artifacts from testrun reports
        match = "Can't create testcase artifacts from testrun"
        with pytest.raises(InvalidReportTypeError, match=match):
            report_handler.get_report_artifact(get_command)

    def test_get_testrun_artifact(self, report_handler, testrun_report):
        """Test retrieving a test run report artifact"""
        # Given: a saved test run report
        location = LocationDTO("dict://test_reports")
        save_command = SaveReportCommand(
            report=testrun_report,
            location=location,
            artifact_format=ReportArtifactFormat.JSON
        )
        report_handler.save_report(save_command)

        # When: trying to retrieve a test run artifact
        command = GetReportArtifactCommand(
            report_id=testrun_report.report_id,
            location=location,
            internal_artifact_format=ReportArtifactFormat.JSON,
            artifact=ReportArtifact.REPORT,
            artifact_format=ReportArtifactFormat.XLSX,
        )

        # Then: an InvalidReportTypeError should be raised because only testcase reports
        # are supported
        # The current implementation only supports testcase reports for artifact creation
        with pytest.raises(
            InvalidReportTypeError,
            match="Can't create testcase artifacts from testrun"
        ):
            report_handler.get_report_artifact(command)

    def test_save_for_users_testcase(self, report_handler, testcase_report):
        """Test saving user artifacts for test case report"""
        # Given: a test case report with diff data and a report handler
        report = testcase_report
        report.diff = {"any_diff": {"a": [1, 2, 3], "b": [4, 5, 6]}}
        report.testtype = TestType.SCHEMA.value
        report.result = TestResult.NOK.value
        location = LocationDTO("dict://user_reports")
        storage = report_handler.storages[0]

        command = SaveReportArtifactsForUsersCommand(
            report=report,
            location=location,
            testcase_report_format=ReportArtifactFormat.TXT,
            testcase_diff_format=ReportArtifactFormat.XLSX,
            testrun_report_format=ReportArtifactFormat.XLSX
        )

        # When: saving user artifacts for the test case report
        report_handler.save_report_artifacts_for_users(command)

        # Then: both report and diff artifacts should be saved to the expected locations
        # Should save report artifact
        date_str = datetime.now().strftime("%Y-%m-%d")
        expected_report_path = location.append(f"{date_str}/{report.testrun_id}/"
            + f"{report.testobject}_{report.testtype}_report.txt")
        report_content = storage.read(expected_report_path)
        assert isinstance(report_content, bytes)

        # Should save diff artifact since testcase has diff
        expected_diff_path = location.append(f"{date_str}/{report.testrun_id}/"
            + f"{report.testobject}_{report.testtype}_diff.xlsx")
        diff_content = storage.read(expected_diff_path)

        # diff artifact should contain all columns and rows
        diff_df = pl.read_excel(diff_content)
        assert diff_df.columns == list(report.diff["any_diff"].keys())
        assert diff_df.shape[0] == len(report.diff["any_diff"]["a"])

    def test_save_for_users_testcase_no_diff(self, report_handler, testcase_report):
        """Test saving user artifacts for test case report without diff"""
        # Given: a test case report without diff data
        report = testcase_report
        report.diff = {}
        report.testtype = TestType.SCHEMA.value
        report.result = TestResult.OK.value
        location = LocationDTO("dict://user_reports")
        storage = report_handler.storages[0]

        command = SaveReportArtifactsForUsersCommand(
            report=report,
            location=location,
            testcase_report_format=ReportArtifactFormat.TXT,
            testcase_diff_format=ReportArtifactFormat.XLSX,
            testrun_report_format=ReportArtifactFormat.XLSX
        )

        # When: saving user artifacts for the test case report without diff
        report_handler.save_report_artifacts_for_users(command)

        # Then: only the report artifact should be saved, no diff artifact
        # Should save report artifact
        date_str = datetime.now().strftime("%Y-%m-%d")
        expected_report_path = location.append(f"{date_str}/{report.testrun_id}/"
            + f"{report.testobject}_{report.testtype}_report.txt")
        report_content = storage.read(expected_report_path)
        assert isinstance(report_content, bytes)

        # Should NOT save diff artifact since no diff
        expected_diff_path = location.append(f"{date_str}/{report.testrun_id}/"
            + f"{report.testobject}_{report.testtype}_diff.xlsx")
        with pytest.raises(ObjectNotFoundError):
            storage.read(expected_diff_path)

    def test_save_for_users_testrun(self, report_handler, testrun_report):
        """Test saving user artifacts for test run report"""
        # Given: a test run report and a report handler
        location = LocationDTO("dict://user_reports")
        command = SaveReportArtifactsForUsersCommand(
            report=testrun_report,
            location=location,
            testcase_report_format=ReportArtifactFormat.TXT,
            testcase_diff_format=ReportArtifactFormat.XLSX,
            testrun_report_format=ReportArtifactFormat.XLSX
        )

        # When: saving user artifacts for the test run report
        report_handler.save_report_artifacts_for_users(command)
        storage = report_handler.storages[0]

        # Then: the test run report artifact should be saved to the expected location
        # Should save report artifact
        date_str = datetime.now().strftime("%Y-%m-%d")
        datetime_str = testrun_report.start_ts.strftime("%Y-%m-%d_%H-%M-%S")
        expected_report_path = location.append(f"{date_str}/{testrun_report.testrun_id}/"
            + f"testrun_report_{datetime_str}.xlsx")

        report_content = storage.read(expected_report_path)
        assert isinstance(report_content, bytes)
        assert report_content.startswith(b"PK\x03\x04")  # XLSX format
