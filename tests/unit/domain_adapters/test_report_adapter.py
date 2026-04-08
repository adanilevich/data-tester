import pytest

from src.domain.report.plugins import (
    TxtTestCaseReportFormatter,
    XlsxTestCaseDiffFormatter,
    XlsxTestRunReportFormatter,
)
from src.domain_adapters import ReportAdapter
from src.domain_ports import (
    CreateTestCaseReportArtifactCommand,
    CreateTestRunReportArtifactCommand,
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
def report_adapter(dto_storage) -> ReportAdapter:
    return ReportAdapter(
        testcase_formatters=[TxtTestCaseReportFormatter(), XlsxTestCaseDiffFormatter()],
        testrun_formatters=[XlsxTestRunReportFormatter()],
        dto_storage=dto_storage,
    )


class TestReportAdapter:
    def test_create_testcase_report_artifact_txt(
        self, report_adapter, dto_storage, testcase_result: TestCaseDTO
    ):
        dto_storage.write_dto(testcase_result)
        command = CreateTestCaseReportArtifactCommand(
            testcase_id=testcase_result.id,
            artifact=ReportArtifact.REPORT,
            artifact_format=ReportArtifactFormat.TXT,
        )
        result = report_adapter.create_testcase_report_artifact(command)

        assert isinstance(result, bytes)
        assert testcase_result.summary in result.decode("utf-8")

    def test_create_testcase_report_artifact_xlsx(
        self, report_adapter, dto_storage, testcase_result: TestCaseDTO
    ):
        dto_storage.write_dto(testcase_result)
        command = CreateTestCaseReportArtifactCommand(
            testcase_id=testcase_result.id,
            artifact=ReportArtifact.DIFF,
            artifact_format=ReportArtifactFormat.XLSX,
        )
        result = report_adapter.create_testcase_report_artifact(command)

        assert isinstance(result, bytes)
        assert result.startswith(b"PK\x03\x04")

    def test_create_testrun_report_artifact_xlsx(
        self, report_adapter, dto_storage, testrun: TestRunDTO
    ):
        dto_storage.write_dto(testrun)
        command = CreateTestRunReportArtifactCommand(
            testrun_id=testrun.id,
            artifact_format=ReportArtifactFormat.XLSX,
        )
        result = report_adapter.create_testrun_report_artifact(command)

        assert isinstance(result, bytes)
        assert result.startswith(b"PK\x03\x04")
