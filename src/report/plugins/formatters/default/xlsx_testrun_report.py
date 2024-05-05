from io import BytesIO
import polars as pl
from src.report.plugins.formatters.default import (
    IReportArtifact,
    ResultTypeNotSupportedError,
)
from src.dtos import (
    TestResultDTO,
    TestRunResultDTO,
    TestRunReportArtifactDTO,
    ArtifactType,
)


class XlsxTestRunReportFormatter(IReportArtifact):
    """
    Excel-based testrun report with only most important info
    """

    artifact_type = ArtifactType.XLSX_TESTRUN_REPORT
    content_type = "application/vnd.opnexmlformats-officedocument.spreadsheetml.template"
    sensitive = False

    def create_artifact(self, result: TestResultDTO) -> TestRunReportArtifactDTO:

        if not isinstance(result, TestRunResultDTO):
            raise ResultTypeNotSupportedError("xlsx only supported for testrun reports")

        results = [
            {
              "Domain": result.testobject.domain,
              "Stage": result.testobject.stage,
              "Instance": result.testobject.instance,
              "Test Object": result.testobject.name,
              "Test Case": result.testtype.value,
              "Test Scenario": result.scenario,
              "Test Result": result.result.value,
              "Execution Status": result.status.value,
              "Summary": result.summary
            } for result in result.testcase_results
        ]
        df = pl.DataFrame(results)
        io = BytesIO()
        df.write_excel(io)
        content_bytes = io.getbuffer().tobytes()
        content_b64_str = self.bytes_to_b64_string(content_bytes)

        artifact = TestRunReportArtifactDTO(
            artifact_type=self.artifact_type,
            sensitive=self.sensitive,
            content_type=self.content_type,
            content_b64_str=content_b64_str,
            testrun_id=result.testrun_id,
            start_ts=result.start_ts,
            result=result.result,
        )

        artifact.filename = self.naming_conventions.filename(artifact=artifact)

        return artifact
