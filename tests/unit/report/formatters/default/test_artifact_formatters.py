import json
from src.report.plugins.formatters.default import (
    JsonTestCaseReportFormatter,
    TxtTestCaseReportFormatter,
    DefaultReportNamingConventions
)
from src.dtos import TestCaseResultDTO


class TestJsonTestCaseReportFormatter:

    def test_that_artefact_is_parseable(self, testcase_result: TestCaseResultDTO):
        # given a json formatter with default naming conventions
        naming_conventions = DefaultReportNamingConventions()
        formatter = JsonTestCaseReportFormatter(naming_conventions=naming_conventions)

        # when a testcase result is provided
        result = testcase_result

        # then it is successfully serialized and formatted to a ReportArtifactDTO
        artifact = formatter.create_artifact(result=result)
        assert artifact.filename is not None
        assert len(artifact.filename) > 5
        content_as_dict = json.loads(artifact.content_b64_str)
        assert "diff" not in content_as_dict
        assert content_as_dict["result"] == result.result.value


class TestTxtTestCaseReportFormatter:

    def test_that_artefact_is_parseable(self, testcase_result: TestCaseResultDTO):
        # given a json formatter with default naming conventions
        naming_conventions = DefaultReportNamingConventions()
        formatter = TxtTestCaseReportFormatter(naming_conventions=naming_conventions)

        # when a testcase result is provided
        result = testcase_result

        # then it is successfully serialized and formatted to a ReportArtifactDTO
        artifact = formatter.create_artifact(result=result)
        assert artifact.filename is not None
        assert len(artifact.filename) > 5
        assert "diff" in artifact.content_b64_str


# class TestExcelTestCaseDiffFormatter:

#     def test_that_artefact_is_parseable(self, testcase_result: TestCaseResultDTO):
#         # given a json formatter with default naming conventions
#         naming_conventions = DefaultReportNamingConventions()
#         formatter = XlsxTestCaseDiffFormatter(naming_conventions=naming_conventions)

#         # when a COMPARE_SAMPLE testcase with NOK result and non-empty diff is provided
#         result = testcase_result
#         result.testtype = TestType.COMPARE_SAMPLE
#         result.result = TestResult.NOK
#         result.diff["compare_sample_diff"] = {"a": [1, 2, 3], "b": ["ab", "bb", "df"]}

#         # then it is successfully serialized and formatted to a ReportArtifactDTO
#         artifact = formatter.create_artifact(result=result)
#         assert artifact.filename is not None
#         assert len(artifact.filename) > 5
#         content = pl.read_excel(artifact.content_b64_str.encode())
#         assert "a" in content.columns
