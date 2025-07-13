import json
import pytest

from src.report.adapters.plugins.json_report import (
    JsonTestCaseReportFormatter,
    JsonTestRunReportFormatter,
)
from src.report.ports.plugins import ReportTypeNotSupportedError
from src.dtos import (
    TestCaseReportDTO,
    TestRunReportDTO,
    ReportArtifactFormat,
    ReportArtifact,
    ReportType,
)


class TestJsonTestCaseReportFormatter:

    def test_properties(self):
        """Test that all properties return correct values"""
        formatter = JsonTestCaseReportFormatter()
        assert formatter.artifact_format == ReportArtifactFormat.JSON
        assert formatter.report_artifact == ReportArtifact.REPORT
        assert formatter.report_type == ReportType.TESTCASE

    def test_create_artifact_with_valid_testcase_report(
        self, testcase_report: TestCaseReportDTO
    ):
        """Test that create_artifact returns valid JSON bytes for TestCaseReportDTO"""
        formatter = JsonTestCaseReportFormatter()

        result = formatter.create_artifact(testcase_report)

        # Should return bytes
        assert isinstance(result, bytes)

        # Should be valid JSON
        json_str = result.decode("utf-8")
        parsed_json = json.loads(json_str)

        # Should contain expected fields
        assert "testrun_id" in parsed_json
        assert "testcase_id" in parsed_json
        assert "result" in parsed_json
        assert "testobject" in parsed_json
        assert "testtype" in parsed_json
        assert "scenario" in parsed_json
        assert "diff" in parsed_json
        assert "summary" in parsed_json
        assert "facts" in parsed_json
        assert "details" in parsed_json
        assert "specifications" in parsed_json
        assert "start_ts" in parsed_json
        assert "end_ts" in parsed_json

        # Should preserve original data
        assert parsed_json["testcase_id"] == str(testcase_report.testcase_id)
        assert parsed_json["testrun_id"] == str(testcase_report.testrun_id)
        assert parsed_json["result"] == testcase_report.result
        assert parsed_json["summary"] == testcase_report.summary

    def test_create_artifact_with_testrun_report_raises_error(
        self, testrun_report: TestRunReportDTO
    ):
        """
        Test that create_artifact raises ReportTypeNotSupportedError
        for TestRunReportDTO"""
        formatter = JsonTestCaseReportFormatter()

        with pytest.raises(ReportTypeNotSupportedError) as exc_info:
            formatter.create_artifact(testrun_report)

        assert "JSON format not supported" in str(exc_info.value)


class TestJsonTestRunReportFormatter:
    def test_artifact_format_property(self):
        """Test that artifact_format returns JSON"""
        formatter = JsonTestRunReportFormatter()
        assert formatter.artifact_format == ReportArtifactFormat.JSON

    def test_report_artifact_property(self):
        """Test that report_artifact returns REPORT"""
        formatter = JsonTestRunReportFormatter()
        assert formatter.report_artifact == ReportArtifact.REPORT

    def test_report_type_property(self):
        """Test that report_type returns TESTRUN"""
        formatter = JsonTestRunReportFormatter()
        assert formatter.report_type == ReportType.TESTRUN

    def test_create_artifact_with_valid_testrun_report(
        self, testrun_report: TestRunReportDTO
    ):
        """Test that create_artifact returns valid JSON bytes for TestRunReportDTO"""
        formatter = JsonTestRunReportFormatter()

        result = formatter.create_artifact(testrun_report)

        # Should return bytes
        assert isinstance(result, bytes)

        # Should be valid JSON
        json_str = result.decode("utf-8")
        parsed_json = json.loads(json_str)

        # Should contain expected fields
        assert "testrun_id" in parsed_json
        assert "result" in parsed_json
        assert "testcase_results" in parsed_json
        assert "start_ts" in parsed_json
        assert "end_ts" in parsed_json

        # Should preserve original data
        assert parsed_json["testrun_id"] == str(testrun_report.testrun_id)
        assert parsed_json["result"] == testrun_report.result
        assert len(parsed_json["testcase_results"]) == len(
            testrun_report.testcase_results
        )

        # Testcase results should have expected structure
        for testcase_result in parsed_json["testcase_results"]:
            assert "testrun_id" in testcase_result
            assert "result" in testcase_result
            assert "testobject" in testcase_result
            assert "testtype" in testcase_result
            assert "summary" in testcase_result
            assert "start_ts" in testcase_result
            assert "end_ts" in testcase_result

    def test_create_artifact_with_testcase_report_raises_error(
        self, testcase_report: TestCaseReportDTO
    ):
        """
        Test that create_artifact raises ReportTypeNotSupportedError for
        TestCaseReportDTO
        """
        formatter = JsonTestRunReportFormatter()

        with pytest.raises(ReportTypeNotSupportedError) as exc_info:
            formatter.create_artifact(testcase_report)

        assert "JSON format not supported" in str(exc_info.value)

    def test_json_output_is_properly_formatted(self, testrun_report: TestRunReportDTO):
        """Test that JSON output is properly formatted with indentation"""
        formatter = JsonTestRunReportFormatter()

        result = formatter.create_artifact(testrun_report)
        json_str = result.decode("utf-8")

        # Should be properly formatted with indentation
        assert json_str.startswith("{\n")
        assert "  " in json_str  # Should have 2-space indentation

        # Should be valid JSON
        parsed_json = json.loads(json_str)
        assert isinstance(parsed_json, dict)
