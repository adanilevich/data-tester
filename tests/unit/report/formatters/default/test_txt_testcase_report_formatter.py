from src.report.adapters.plugins.formatters.default import (
    TxtTestCaseReportFormatter,
    DefaultReportNamingConventions,
)
from src.dtos import TestCaseResultDTO, TestType

class TestTxtTestCaseReportFormatter:
    def test_that_artefact_is_parseable(self, testcase_result: TestCaseResultDTO):
        # given a txt formatter with default naming conventions
        naming_conventions = DefaultReportNamingConventions()
        formatter = TxtTestCaseReportFormatter(naming_conventions=naming_conventions)

        # when a testcase result is provided
        result = testcase_result

        # and the testcase is not a compare_sample testcase
        for testtype in [TestType.SCHEMA, TestType.ROWCOUNT]:
            result.testtype = testtype

            # then it is successfully serialized and formatted to a ReportArtifactDTO
            artifact = formatter.create_artifact(result=result)
            assert artifact.filename is not None
            assert len(artifact.filename) > 5

            # and when the content is correctly decoded
            content_as_b64_str = artifact.content_b64_str
            content_as_yaml_bytes = formatter.b64_string_to_bytes(content_as_b64_str)
            content_as_dict = formatter.yaml_bytes_to_dict(content_as_yaml_bytes)

            # then diff is included for non-compare_sample testcases
            assert "diff" in content_as_dict

            # and specifications are excluded for non-compare_sample testcases
            assert "specifications" not in content_as_dict

    def test_that_diff_is_excluded_for_compare_sample_testcases(
        self, testcase_result: TestCaseResultDTO
    ):
        # given a txt formatter with default naming conventions
        naming_conventions = DefaultReportNamingConventions()
        formatter = TxtTestCaseReportFormatter(naming_conventions=naming_conventions)

        # when a testcase result is provided
        result = testcase_result

        # and the testcase is a compare_sample testcase
        result.testtype = TestType.COMPARE_SAMPLE

        # then it is successfully serialized and formatted to a ReportArtifactDTO
        artifact = formatter.create_artifact(result=result)
        assert artifact.filename is not None
        assert len(artifact.filename) > 5

        # and when the content is correctly decoded
        content_as_b64_str = artifact.content_b64_str
        content_as_yaml_bytes = formatter.b64_string_to_bytes(content_as_b64_str)
        content_as_dict = formatter.yaml_bytes_to_dict(content_as_yaml_bytes)

        # then result is correctly set
        assert content_as_dict["result"] == result.result.value

        # then specifications are excluded
        assert "specifications" not in content_as_dict

        # and diff is excluded
        assert "diff" not in artifact.content_b64_str
