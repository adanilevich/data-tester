from src.report.adapters.plugins.formatters.default import (
    JsonTestCaseReportFormatter,
    DefaultReportNamingConventions,
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
