from typing import Dict, Type
import pytest
from base64 import b64encode
from uuid import uuid4
from datetime import datetime
from src.report.adapters.plugins.formatters.default import (
    DefaultReportFormatter,
    IReportArtifact,
    DefaultReportNamingConventions,
    ArtifactTypeUnknownError,
)
from src.dtos import (
    ReportArtifactDTO,
    ArtifactType,
    TestResult,
    TestCaseResultDTO,
    TestResultDTO,
    TestType,
)


artifact = ReportArtifactDTO(
    testrun_id=uuid4(),
    artifact_type=ArtifactType.XLSX_TESTCASE_DIFF,
    sensitive=False,
    content_type="plain/text",
    content_b64_str=b64encode(b"my_content").decode(),
    start_ts=datetime.now(),
    result=TestResult.OK,
)


class DummyArtifact(IReportArtifact):
    def create_artifact(self, result: TestResultDTO) -> ReportArtifactDTO:
        return artifact.create_copy()


class TestDefaultReportFormatter:
    @pytest.fixture
    def formatter_config(self) -> Dict[ArtifactType, Type[IReportArtifact]]:
        # formatter will not know TXT_TESTCASE_REPORT and always return DummyArtifact
        return {
            ArtifactType.XLSX_TESTCASE_DIFF: DummyArtifact,
            ArtifactType.XLSX_TESTRUN_REPORT: DummyArtifact,
            ArtifactType.JSON_TESTCASE_REPORT: DummyArtifact,
        }

    @pytest.fixture
    def formatter(self, formatter_config) -> DefaultReportFormatter:
        return DefaultReportFormatter(
            naming_conventions=DefaultReportNamingConventions(),
            config=formatter_config,
        )

    def test_that_requesting_unknown_artifact_types_raises_error(
        self, formatter: DefaultReportFormatter, testrun_result
    ):
        # given a DefaultReportFormatter
        formatter = formatter

        # when formatter doesnt support one artifact type, e.g. TXT_REPORT
        assert ArtifactType.TXT_TESTCASE_REPORT not in formatter.config

        # and the unsupported artifact type is requested
        requested_artifact_types = [
            ArtifactType.JSON_TESTCASE_REPORT,
            ArtifactType.TXT_TESTCASE_REPORT,
        ]

        # then creating artifacts raises an error
        with pytest.raises(ArtifactTypeUnknownError):
            _ = formatter.create_artifacts(
                result=testrun_result,
                artifact_types=requested_artifact_types)

    def test_that_xlsx_diff_is_only_returned_for_compare_sample_nok(
        self, formatter: DefaultReportFormatter, testcase_result: TestCaseResultDTO,
        testrun_result
    ):
        # given a DefaultReportFormatter
        formatter = formatter

        # when an xlsx-based testcase_diff is requested ...
        requested_artifact_types = [ArtifactType.XLSX_TESTCASE_DIFF]

        # ... for a COMPARE_SAMPLE testcase with OK result
        result = testcase_result
        result.testtype = TestType.COMPARE_SAMPLE
        result.result = TestResult.OK

        # then requesting the artifact leads to an empty result list
        artifacts = formatter.create_artifacts(
            result=result,
            artifact_types=requested_artifact_types
        )
        assert len(artifacts) == 0

        # ... however if the COMPARE_SAMPLE testcase has NOK result
        result = testcase_result
        result.testtype = TestType.COMPARE_SAMPLE
        result.result = TestResult.NOK

        # then requesting the artifact leads returns exactly one artifact
        artifacts = formatter.create_artifacts(
            result=result,
            artifact_types=requested_artifact_types
        )
        assert len(artifacts) == 1

        # ... and if the xlsx diff is requested for a testrun result
        result = testrun_result

        # then requesting the artifact returns an empty list
        artifacts = formatter.create_artifacts(
            result=result,
            artifact_types=requested_artifact_types
        )
        assert len(artifacts) == 0
