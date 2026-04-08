import yaml

from src.domain.report.plugins import TxtTestCaseReportFormatter
from src.dtos import ReportArtifact, ReportArtifactFormat, TestCaseDTO


class TestTxtTestCaseReportFormatter:
    def test_properties(self):
        formatter = TxtTestCaseReportFormatter()
        assert formatter.artifact_format == ReportArtifactFormat.TXT
        assert formatter.artifact == ReportArtifact.REPORT

    def test_create_artifact_with_valid_testcase(self, testcase_result: TestCaseDTO):
        formatter = TxtTestCaseReportFormatter()
        result = formatter.create_artifact(testcase_result)

        assert isinstance(result, bytes)
        parsed_yaml = yaml.safe_load(result.decode("utf-8"))

        assert "result" in parsed_yaml
        assert "testobject" in parsed_yaml
        assert "testtype" in parsed_yaml
        assert "summary" in parsed_yaml
        assert "facts" in parsed_yaml
        assert "details" in parsed_yaml
        assert "start_ts" in parsed_yaml
        assert "end_ts" in parsed_yaml
        assert "specs" in parsed_yaml
        assert isinstance(parsed_yaml["specs"], list)
        assert parsed_yaml["result"] == testcase_result.result.value
        assert parsed_yaml["summary"] == testcase_result.summary

    def test_diff_excluded_for_non_schema(self, testcase_result: TestCaseDTO):
        from src.dtos import TestType

        formatter = TxtTestCaseReportFormatter()
        # override testtype to COMPARE (non-SCHEMA)
        tc = testcase_result.model_copy(update={"testtype": TestType.COMPARE})
        result = formatter.create_artifact(tc)
        parsed_yaml = yaml.safe_load(result.decode("utf-8"))
        # diff not included for non-SCHEMA
        assert "diff" not in parsed_yaml
        assert "specs" in parsed_yaml

    def test_schema_diff_included_simplified(self, testcase_result: TestCaseDTO):
        from src.dtos import TestType

        tc = testcase_result.model_copy(
            update={
                "testtype": TestType.SCHEMA,
                "diff": {
                    "column_diff": [
                        {
                            "expected_column": "id",
                            "expected_dtype": "int",
                            "actual_column": "id",
                            "actual_dtype": "int",
                            "result_all": "OK",
                        },
                        {
                            "expected_column": "name",
                            "expected_dtype": "string",
                            "actual_column": "name",
                            "actual_dtype": "int",
                            "result_all": "NOK",
                        },
                    ],
                    "partitioning_diff": {
                        "expected_partitioning": ["date"],
                        "actual_partitioning": ["date", "region"],
                    },
                },
            }
        )
        formatter = TxtTestCaseReportFormatter()
        result = formatter.create_artifact(tc)
        parsed_yaml = yaml.safe_load(result.decode("utf-8"))

        assert "diff" in parsed_yaml
        assert "column_diff" in parsed_yaml["diff"]
        assert len(parsed_yaml["diff"]["column_diff"]) == 1
        assert parsed_yaml["diff"]["column_diff"][0]["column"] == "name"
        assert "partitioning_diff" in parsed_yaml["diff"]

    def test_schema_diff_omits_equal_sections(self, testcase_result: TestCaseDTO):
        from src.dtos import TestType

        tc = testcase_result.model_copy(
            update={
                "testtype": TestType.SCHEMA,
                "diff": {
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
                },
            }
        )
        formatter = TxtTestCaseReportFormatter()
        result = formatter.create_artifact(tc)
        parsed_yaml = yaml.safe_load(result.decode("utf-8"))

        assert parsed_yaml.get("diff") == {} or "diff" not in parsed_yaml
