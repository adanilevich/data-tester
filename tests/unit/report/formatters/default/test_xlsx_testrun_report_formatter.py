import pytest
from src.report.adapters.plugins.formatters.default import (
    XlsxTestRunReportFormatter,
    DefaultReportNamingConventions,
)
from src.report.adapters.plugins.formatters.default.i_report_artifact import (
    ResultTypeNotSupportedError
)

class TestXlsxTestRunReportFormatter:
    def test_that_artefact_is_parseable(self, testrun_result):
        # given an xlsx testrun formatter with default naming conventions
        naming_conventions = DefaultReportNamingConventions()
        formatter = XlsxTestRunReportFormatter(naming_conventions=naming_conventions)

        # when a testrun result is provided
        result = testrun_result

        # then it is successfully serialized and formatted to a TestRunReportArtifactDTO
        artifact = formatter.create_artifact(result=result)
        assert artifact.filename is not None
        assert len(artifact.filename) > 5
        assert artifact.artifact_type.value == "xlsx-testrun-report"
        assert artifact.content_type.startswith("application/vnd")
        assert artifact.testrun_id == result.testrun_id
        assert artifact.result == result.result
        assert artifact.start_ts == result.start_ts

        # and when the content is correctly decoded
        content_as_b64_str = artifact.content_b64_str
        content_as_excel_bytes = formatter.b64_string_to_bytes(content_as_b64_str)
        content_as_dict = formatter.excel_bytes_to_dict(content_as_excel_bytes)

        # then the Excel content should have the expected columns and rows
        assert isinstance(content_as_dict, dict)
        expected_columns = [
            "Domain", "Stage", "Instance", "Test Object", "Test Case",
            "Test Scenario", "Test Result", "Execution Status", "Summary"
        ]
        for col in expected_columns:
            assert col in content_as_dict
        num_rows = len(result.testcase_results)
        for col in expected_columns:
            assert len(content_as_dict[col]) == num_rows

    def test_that_wrong_type_raises(self, testcase_result):
        # given an xlsx testrun formatter with default naming conventions
        naming_conventions = DefaultReportNamingConventions()
        formatter = XlsxTestRunReportFormatter(naming_conventions=naming_conventions)
        # when a TestCaseResultDTO is provided instead of TestRunResultDTO
        with pytest.raises(ResultTypeNotSupportedError):
            formatter.create_artifact(result=testcase_result)
