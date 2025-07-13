import yaml  # type: ignore
import pytest

from src.report.adapters.plugins.txt_testcase_report import TxtTestCaseReportFormatter
from src.report.ports.plugins import ReportTypeNotSupportedError
from src.dtos import (
    TestCaseReportDTO,
    TestRunReportDTO,
    ReportArtifactFormat,
    ReportArtifact,
    ReportType,
)


class TestTxtTestCaseReportFormatter:

    def test_properties(self):
        # given a TxtTestCaseReportFormatter instance
        formatter = TxtTestCaseReportFormatter()
        # then all properties should have correct values
        assert formatter.artifact_format == ReportArtifactFormat.TXT
        assert formatter.report_artifact == ReportArtifact.REPORT
        assert formatter.report_type == ReportType.TESTCASE

    def test_create_artifact_with_valid_testcase_report(
        self, testcase_report: TestCaseReportDTO
    ):
        # given a valid TestCaseReportDTO and formatter
        formatter = TxtTestCaseReportFormatter()
        # when create_artifact is called
        result = formatter.create_artifact(testcase_report)
        # then it should return valid YAML bytes
        assert isinstance(result, bytes)
        yaml_str = result.decode("utf-8")
        parsed_yaml = yaml.safe_load(yaml_str)
        # then YAML should contain expected fields
        assert "testrun_id" in parsed_yaml
        assert "testcase_id" in parsed_yaml
        assert "result" in parsed_yaml
        assert "testobject" in parsed_yaml
        assert "testtype" in parsed_yaml
        assert "scenario" in parsed_yaml
        assert "summary" in parsed_yaml
        assert "facts" in parsed_yaml
        assert "details" in parsed_yaml
        assert "start_ts" in parsed_yaml
        assert "end_ts" in parsed_yaml
        # then YAML should preserve original data
        assert parsed_yaml["testcase_id"] == str(testcase_report.testcase_id)
        assert parsed_yaml["testrun_id"] == str(testcase_report.testrun_id)
        assert parsed_yaml["result"] == testcase_report.result
        assert parsed_yaml["summary"] == testcase_report.summary
        # then YAML should exclude specifications and diff
        assert "specifications" not in parsed_yaml
        assert "diff" not in parsed_yaml

    def test_create_artifact_with_testrun_report_raises_error(
        self, testrun_report: TestRunReportDTO
    ):
        # given a TxtTestCaseReportFormatter and a TestRunReportDTO (invalid type)
        formatter = TxtTestCaseReportFormatter()
        # when create_artifact is called with wrong type
        with pytest.raises(ReportTypeNotSupportedError) as exc_info:
            formatter.create_artifact(testrun_report)
        # then it should raise ReportTypeNotSupportedError
        assert "Txt format not supported" in str(exc_info.value)

    def test_excluded_fields_are_not_present(self, testcase_report: TestCaseReportDTO):
        # given a TxtTestCaseReportFormatter and a valid TestCaseReportDTO
        formatter = TxtTestCaseReportFormatter()
        # when create_artifact is called
        result = formatter.create_artifact(testcase_report)
        yaml_str = result.decode("utf-8")
        parsed_yaml = yaml.safe_load(yaml_str)
        # then specifications and diff should be excluded
        assert "specifications" not in parsed_yaml
        assert "diff" not in parsed_yaml
        # then other fields should still be present
        assert "testcase_id" in parsed_yaml
        assert "testrun_id" in parsed_yaml
        assert "result" in parsed_yaml
        assert "summary" in parsed_yaml
