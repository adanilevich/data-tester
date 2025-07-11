from src.report.adapters.plugins.formatters.default import (
    IReportArtifact,
    ResultTypeNotSupportedError,
    ReportArtifactError
)
from src.dtos import (
    TestResultDTO,
    TestCaseResultDTO,
    TestCaseReportArtifactDTO,
    ArtifactType,
    TestType,
    TestResult
)


class XlsxTestCaseDiffFormatter(IReportArtifact):
    """
    Excel-based diff of a compare_sample testcase
    """

    artifact_type = ArtifactType.XLSX_TESTCASE_DIFF
    content_type = "application/vnd.opnexmlformats-officedocument.spreadsheetml.template"
    sensitive = True

    def create_artifact(self, result: TestResultDTO) -> TestCaseReportArtifactDTO:
        """Creates a xlsx-based diff of a testcase"""

        if not isinstance(result, TestCaseResultDTO):
            raise ResultTypeNotSupportedError(f"Xlsx diff not supported for {result}")

        msg = "Xlsx diff only supported for NOK COMPARE_SAMPLE"
        if not result.testtype == TestType.COMPARE_SAMPLE:
            raise ReportArtifactError(msg)

        if not result.result == TestResult.NOK:
            raise ReportArtifactError(msg)

        if result.diff.get("compare_sample_diff") is None:
            raise ReportArtifactError("Compare sample diff is not provided")

        # apply dict() to avoid type hint issue with polars since diff entry is declared
        # as dict[Any, Any] or list[Any]
        diff_as_dict = dict(result.diff["compare_sample_diff"])
        diff_as_excel_bytes = self.dict_to_excel_bytes(diff_as_dict)
        diff_as_b64_str = self.bytes_to_b64_string(diff_as_excel_bytes)

        artifact = TestCaseReportArtifactDTO(
            artifact_type=self.artifact_type,
            sensitive=self.sensitive,
            content_type=self.content_type,
            content_b64_str=diff_as_b64_str,
            testrun_id=result.testrun_id,
            start_ts=result.start_ts,
            result=result.result,
            testcase_id=result.testcase_id,
            testobject=result.testobject,
            testcase=result.testtype,
        )

        artifact.filename = self.naming_conventions.filename(artifact=artifact)

        return artifact
