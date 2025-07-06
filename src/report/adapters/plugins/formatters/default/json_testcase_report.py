from src.report.adapters.plugins.formatters.default import (
    IReportArtifact,
    ResultTypeNotSupportedError,
)
from src.dtos import (
    TestResultDTO,
    TestCaseResultDTO,
    TestCaseReportArtifactDTO,
    ArtifactType,
)


class JsonTestCaseReportFormatter(IReportArtifact):
    """
    Json-based testcase report without diff, details and specs
    """

    artifact_type = ArtifactType.JSON_TESTCASE_REPORT
    content_type = "application/json"
    sensitive = False

    def create_artifact(self, result: TestResultDTO) -> TestCaseReportArtifactDTO:
        """
        Creates a json-based testcase report artifact without diff, details
        and specifications
        """

        if not isinstance(result, TestCaseResultDTO):
            raise ResultTypeNotSupportedError(f"Json format not supported for {result}")

        exclude = {"diff", "details", "specifications"}

        content_bytes = result.to_json(exclude=exclude).encode()
        content_b64_str = self.bytes_to_b64_string(content_bytes)

        artifact = TestCaseReportArtifactDTO(
            artifact_type=self.artifact_type,
            sensitive=self.sensitive,
            content_type=self.content_type,
            content_b64_str=content_b64_str,
            testrun_id=result.testrun_id,
            start_ts=result.start_ts,
            result=result.result,
            testcase_id=result.testcase_id,
            testobject=result.testobject,
            testcase=result.testtype,
        )

        artifact.filename = self.naming_conventions.filename(artifact=artifact)

        return artifact
