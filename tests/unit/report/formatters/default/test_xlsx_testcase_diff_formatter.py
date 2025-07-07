from src.report.adapters.plugins.formatters.default import (
    XlsxTestCaseDiffFormatter,
    DefaultReportNamingConventions,
)
from src.dtos import TestCaseResultDTO, TestType, TestResult

class TestExcelTestCaseDiffFormatter:
    def test_that_artefact_is_parseable(self, testcase_result: TestCaseResultDTO):
        # given an xlsx diff formatter with default naming conventions
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
