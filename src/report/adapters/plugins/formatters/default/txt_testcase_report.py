import yaml  # type: ignore
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


class TxtTestCaseReportFormatter(IReportArtifact):
    """
    Txt-based testcase report with diff, details but without
    """

    artifact_type = ArtifactType.TXT_TESTCASE_REPORT
    content_type = "text/plain"
    sensitive = False

    def create_artifact(self, result: TestResultDTO) -> TestCaseReportArtifactDTO:
        """Creates a json-based testcaser report artifact without diff and details"""

        if not isinstance(result, TestCaseResultDTO):
            raise ResultTypeNotSupportedError(f"Json format not supported for {result}")

        content_dict = result.to_dict(exclude={"specifications"}, mode="json")

        content_bytes = yaml.safe_dump(
            data=content_dict,
            default_flow_style=False,
            indent=4,
            encoding="utf-8"
        )
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
