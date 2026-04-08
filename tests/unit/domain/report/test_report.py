import pytest

from src.domain.report import (
    NoFormatterFoundError,
    Report,
    ReportError,
)
from src.domain.report.plugins import (
    TxtTestCaseReportFormatter,
    XlsxTestCaseDiffFormatter,
    XlsxTestRunReportFormatter,
)
from src.dtos import (
    LocationDTO,
    ReportArtifact,
    ReportArtifactFormat,
    TestCaseDTO,
    TestRunDTO,
)
from src.infrastructure.storage.dto_storage_file import JsonSerializer, MemoryDtoStorage


@pytest.fixture
def dto_storage() -> MemoryDtoStorage:
    return MemoryDtoStorage(
        serializer=JsonSerializer(),
        storage_location=LocationDTO("memory://test/"),
    )


@pytest.fixture
def report(dto_storage):
    return Report(
        testcase_formatters=[TxtTestCaseReportFormatter(), XlsxTestCaseDiffFormatter()],
        testrun_formatters=[XlsxTestRunReportFormatter()],
        dto_storage=dto_storage,
    )


class TestReport:
    def test_duplicate_testcase_formatter_raises(self, dto_storage):
        with pytest.raises(ReportError, match="already registered"):
            Report(
                testcase_formatters=[
                    TxtTestCaseReportFormatter(),
                    TxtTestCaseReportFormatter(),
                ],
                testrun_formatters=[],
                dto_storage=dto_storage,
            )

    def test_duplicate_testrun_formatter_raises(self, dto_storage):
        with pytest.raises(ReportError, match="already registered"):
            Report(
                testcase_formatters=[],
                testrun_formatters=[
                    XlsxTestRunReportFormatter(),
                    XlsxTestRunReportFormatter(),
                ],
                dto_storage=dto_storage,
            )

    def test_create_testcase_report_artifact_txt(
        self, report, dto_storage, testcase_result: TestCaseDTO
    ):
        dto_storage.write_dto(testcase_result)
        artifact = report.create_testcase_report_artifact(
            testcase_id=str(testcase_result.id),
            artifact=ReportArtifact.REPORT,
            artifact_format=ReportArtifactFormat.TXT,
        )
        assert isinstance(artifact, bytes)
        assert testcase_result.summary in artifact.decode("utf-8")

    def test_create_testcase_report_artifact_xlsx_diff(
        self, report, dto_storage, testcase_result: TestCaseDTO
    ):
        dto_storage.write_dto(testcase_result)
        artifact = report.create_testcase_report_artifact(
            testcase_id=str(testcase_result.id),
            artifact=ReportArtifact.DIFF,
            artifact_format=ReportArtifactFormat.XLSX,
        )
        assert isinstance(artifact, bytes)
        assert artifact.startswith(b"PK\x03\x04")

    def test_create_testrun_report_artifact_xlsx(
        self, report, dto_storage, testrun: TestRunDTO
    ):
        dto_storage.write_dto(testrun)
        artifact = report.create_testrun_report_artifact(
            testrun_id=str(testrun.id),
            artifact_format=ReportArtifactFormat.XLSX,
        )
        assert isinstance(artifact, bytes)
        assert artifact.startswith(b"PK\x03\x04")

    def test_create_testcase_artifact_no_formatter(
        self, report, dto_storage, testcase_result: TestCaseDTO
    ):
        dto_storage.write_dto(testcase_result)
        with pytest.raises(NoFormatterFoundError):
            report.create_testcase_report_artifact(
                testcase_id=str(testcase_result.id),
                artifact=ReportArtifact.REPORT,
                artifact_format=ReportArtifactFormat.XLSX,
            )

    def test_create_testcase_artifact_not_found(self, report):
        from uuid import uuid4

        from src.infrastructure_ports import ObjectNotFoundError

        with pytest.raises(ObjectNotFoundError):
            report.create_testcase_report_artifact(
                testcase_id=str(uuid4()),
                artifact=ReportArtifact.REPORT,
                artifact_format=ReportArtifactFormat.TXT,
            )

    def test_create_testrun_artifact_no_formatter(
        self, dto_storage, testrun: TestRunDTO
    ):
        r = Report(
            testcase_formatters=[],
            testrun_formatters=[],
            dto_storage=dto_storage,
        )
        dto_storage.write_dto(testrun)
        with pytest.raises(NoFormatterFoundError):
            r.create_testrun_report_artifact(
                testrun_id=str(testrun.id),
                artifact_format=ReportArtifactFormat.XLSX,
            )
