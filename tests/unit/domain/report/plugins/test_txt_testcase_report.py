import yaml
import pytest

from src.domain.report.plugins import (
    TxtTestCaseReportFormatter,
    ReportTypeNotSupportedError,
)
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
        assert "summary" in parsed_yaml
        assert "facts" in parsed_yaml
        assert "details" in parsed_yaml
        assert "start_ts" in parsed_yaml
        assert "end_ts" in parsed_yaml
        # then specifications should be present as simplified file paths
        assert "specifications" in parsed_yaml
        assert isinstance(parsed_yaml["specifications"], list)
        # then YAML should preserve original data
        assert parsed_yaml["testcase_id"] == str(testcase_report.testcase_id)
        assert parsed_yaml["testrun_id"] == str(testcase_report.testrun_id)
        assert parsed_yaml["result"] == testcase_report.result
        assert parsed_yaml["summary"] == testcase_report.summary

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

    def test_diff_excluded_for_non_schema(self, testcase_report: TestCaseReportDTO):
        # given a non-SCHEMA testcase report
        testcase_report.testtype = "COMPARE"
        formatter = TxtTestCaseReportFormatter()
        # when create_artifact is called
        result = formatter.create_artifact(testcase_report)
        parsed_yaml = yaml.safe_load(result.decode("utf-8"))
        # then diff should not be present (goes to XLSX diff formatter)
        assert "diff" not in parsed_yaml
        # but specifications should still be present
        assert "specifications" in parsed_yaml

    def test_schema_diff_included_simplified(self, testcase_report: TestCaseReportDTO):
        # given a SCHEMA testcase report with diffs
        testcase_report.testtype = "SCHEMA"
        testcase_report.diff = {
            "column_diff": [
                {
                    "expected_column": "id",
                    "expected_dtype": "int",
                    "actual_column": "id",
                    "actual_dtype": "int",
                    "result_column": "OK",
                    "result_dtype": "OK",
                    "result_all": "OK",
                },
                {
                    "expected_column": "name",
                    "expected_dtype": "string",
                    "actual_column": "name",
                    "actual_dtype": "int",
                    "result_column": "OK",
                    "result_dtype": "NOK",
                    "result_all": "NOK",
                },
            ],
            "partitioning_diff": {
                "expected_partitioning": ["date"],
                "actual_partitioning": ["date", "region"],
            },
        }
        formatter = TxtTestCaseReportFormatter()
        # when create_artifact is called
        result = formatter.create_artifact(testcase_report)
        parsed_yaml = yaml.safe_load(result.decode("utf-8"))
        # then diff should be present with only NOK columns
        assert "diff" in parsed_yaml
        assert "column_diff" in parsed_yaml["diff"]
        assert len(parsed_yaml["diff"]["column_diff"]) == 1
        assert parsed_yaml["diff"]["column_diff"][0]["column"] == "name"
        # and partitioning diff should be included (different values)
        assert "partitioning_diff" in parsed_yaml["diff"]

    def test_schema_diff_omits_equal_sections(
        self, testcase_report: TestCaseReportDTO,
    ):
        # given a SCHEMA testcase report where partitioning is equal
        testcase_report.testtype = "SCHEMA"
        testcase_report.diff = {
            "column_diff": [
                {
                    "expected_column": "id",
                    "expected_dtype": "int",
                    "actual_column": "id",
                    "actual_dtype": "int",
                    "result_all": "OK",
                },
            ],
            "partitioning_diff": {
                "expected_partitioning": ["date"],
                "actual_partitioning": ["date"],
            },
        }
        formatter = TxtTestCaseReportFormatter()
        result = formatter.create_artifact(testcase_report)
        parsed_yaml = yaml.safe_load(result.decode("utf-8"))
        # then diff should be empty (all OK columns, equal partitioning)
        # an empty dict is falsy but still present in the YAML as {}
        assert parsed_yaml.get("diff") == {} or "diff" not in parsed_yaml
