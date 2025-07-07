from src.report.adapters.plugins.formatters.default import (
    JsonTestCaseReportFormatter,
    TxtTestCaseReportFormatter,
    XlsxTestCaseDiffFormatter,
    DefaultReportNamingConventions,
)
from src.dtos import TestCaseResultDTO, TestType , TestResult


class TestJsonTestCaseReportFormatter:

    def test_that_artefact_is_parseable(self, testcase_result: TestCaseResultDTO):
        """
        Test that the artifact is successfully serialized and formatted to a
        ReportArtifactDTO and that diff and specifications are excluded.
        """
        # given a json formatter with default naming conventions
        naming_conventions = DefaultReportNamingConventions()
        formatter = JsonTestCaseReportFormatter(naming_conventions=naming_conventions)

        # when a testcase result is provided
        result = testcase_result

        # then it is successfully serialized and formatted to a ReportArtifactDTO
        artifact = formatter.create_artifact(result=result)
        assert artifact.filename is not None
        assert len(artifact.filename) > 5

        # and when the content is correctly decoded
        content_as_b64_str = artifact.content_b64_str
        content_as_bytes = formatter.b64_string_to_bytes(content_as_b64_str)
        content_as_dict = formatter.json_bytes_to_dict(content_as_bytes)

        # then diff is excluded
        assert "diff" not in content_as_dict

        # and specifications are excluded
        assert "specifications" not in content_as_dict

        # and result is correctly set
        assert content_as_dict["result"] == result.result.value


class TestTxtTestCaseReportFormatter:

    def test_that_artefact_is_parseable(self, testcase_result: TestCaseResultDTO):
        """
        Test that the artifact is successfully serialized and formatted to a
        ReportArtifactDTO and that diff is included for non-compare_sample testcases
        and that specifications are excluded.
        """
        # given a json formatter with default naming conventions
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
        """
        Test that the artifact is successfully serialized and formatted to a
        ReportArtifactDTO and that diff is excluded for compare_sample testcases.
        """
        # given a json formatter with default naming conventions
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

# TODO: fix this test
class TestExcelTestCaseDiffFormatter:

    def test_that_artefact_is_parseable(self, testcase_result: TestCaseResultDTO):
        # given a json formatter with default naming conventions
        naming_conventions = DefaultReportNamingConventions()
        formatter = XlsxTestCaseDiffFormatter(naming_conventions=naming_conventions)

        # when a COMPARE_SAMPLE testcase with NOK result and non-empty diff is provided
        result = testcase_result
        result.testtype = TestType.COMPARE_SAMPLE
        result.result = TestResult.NOK
        result.diff["compare_sample_diff"] = {"a": [1, 2, 3], "b": ["ab", "bb", "df"]}

        # then it is successfully serialized and formatted to a ReportArtifactDTO
        artifact = formatter.create_artifact(result=result)
        assert artifact.filename is not None
        assert len(artifact.filename) > 5

        # and when the content is correctly decoded
        content_as_b64_str = artifact.content_b64_str
        content_as_excel_bytes = formatter.b64_string_to_bytes(content_as_b64_str)
        content_as_dict = formatter.excel_bytes_to_dict(content_as_excel_bytes)

        # then the diff is correctly set
        assert content_as_dict["a"] == [1, 2, 3]
        assert content_as_dict["b"] == ["ab", "bb", "df"]
