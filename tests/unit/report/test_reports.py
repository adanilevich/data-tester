import json
import os
from typing import Dict, List
from unittest.mock import Mock

import pytest

from src.report.core.report import (
    Report,
    NoFormatterFoundError,
    ReportArtifactNotSpecifiedError,
    WrongReportTypeError,
)
from src.report.ports.infrastructure import IStorage, StorageTypeUnknownError
from src.report.adapters.plugins import (
    JsonTestCaseReportFormatter,
    JsonTestRunReportFormatter,
    TxtTestCaseReportFormatter,
    XlsxTestRunReportFormatter,
    XlsxTestCaseDiffFormatter,
)
from src.dtos import (
    TestCaseReportDTO,
    TestRunReportDTO,
    ReportArtifact,
    ReportArtifactFormat,
)


class DictStorage(IStorage):
    """Mock storage implementation for testing"""

    def __init__(self):
        self.store: Dict[str, bytes] = {}

    def read(self, path: str) -> bytes:
        return self.store[path]

    def write(self, content: bytes, path: str):
        self.store[path] = content

    @property
    def supported_storage_types(self) -> List[str]:
        return ["dict"]

@pytest.fixture
def formatters():
    """Create formatters as defined in config.py"""
    return [
        JsonTestCaseReportFormatter(),
        JsonTestRunReportFormatter(),
        TxtTestCaseReportFormatter(),
        XlsxTestRunReportFormatter(),
        XlsxTestCaseDiffFormatter(),
    ]


@pytest.fixture
def report(formatters):
    return Report(formatters=formatters, storages=[DictStorage()])


class TestReport:
    def test_initialization_with_formatters_and_storages(self, formatters):
        # given formatters and storages
        formatters = formatters
        storage = DictStorage()

        # when initializing Report with formatters and storages
        report = Report(formatters=formatters, storages=[storage])

        # then formatters and storages are properly registered
        assert len(report.formatters) == 5
        assert len(report.storages) == 1
        assert "dict" in report.storages_by_type
        assert len(report.formatters_by_type_artifact_and_format) == 5

    def test_initialization_with_duplicate_formatter(self):
        # given duplicate formatters and correct storage
        duplicate_formatters = [
            JsonTestCaseReportFormatter(),
            JsonTestCaseReportFormatter(),
        ]
        storage = DictStorage()

        # then initialization raises ValueError
        with pytest.raises(ValueError, match="Formatter.*already registered"):
            Report(formatters=duplicate_formatters, storages=[storage])  # type: ignore

    def test_initialization_with_duplicate_storage_type(self):
        # given storages with duplicate storage types
        storage1 = DictStorage()
        storage2 = DictStorage()

        # then initialization raises ValueError
        with pytest.raises(ValueError, match="Storage type.*already registered"):
            Report(formatters=[], storages=[storage1, storage2])

    def test_create_report_from_testcase_result(self, report, testcase_result):
        # when creating a report from testcase result
        report_dto = report.create_report(testcase_result)

        # then it returns a TestCaseReportDTO
        assert isinstance(report_dto, TestCaseReportDTO)
        assert report_dto.testcase_id == testcase_result.testcase_id
        assert report_dto.testrun_id == testcase_result.testrun_id
        assert report_dto.testobject == testcase_result.testobject.name
        assert report_dto.testtype == testcase_result.testtype.value
        assert report_dto.scenario == testcase_result.scenario
        assert report_dto.diff == testcase_result.diff
        assert report_dto.summary == testcase_result.summary
        assert report_dto.facts == testcase_result.facts
        assert report_dto.details == testcase_result.details
        assert report_dto.specifications == testcase_result.specifications
        assert report_dto.result == testcase_result.result.value
        assert report_dto.start_ts == testcase_result.start_ts
        assert report_dto.end_ts == testcase_result.end_ts

    def test_create_report_from_testrun_result(self, report, testrun_result):
        # when creating a report from testrun result
        report_dto = report.create_report(testrun_result)

        # then it returns a TestRunReportDTO
        assert isinstance(report_dto, TestRunReportDTO)
        assert report_dto.testrun_id == testrun_result.testrun_id
        assert report_dto.result == testrun_result.result.value
        assert report_dto.start_ts == testrun_result.start_ts
        assert report_dto.end_ts == testrun_result.end_ts
        assert len(report_dto.testcase_results) == len(testrun_result.testcase_results)

        # then the testcase results are correctly converted
        for i, testcase_result in enumerate(testrun_result.testcase_results):
            dto_testcase = report_dto.testcase_results[i]
            assert dto_testcase.testrun_id == testcase_result.testrun_id
            assert dto_testcase.testobject == testcase_result.testobject.name
            assert dto_testcase.testtype == testcase_result.testtype.value
            assert dto_testcase.summary == testcase_result.summary
            assert dto_testcase.result == testcase_result.result.value
            assert dto_testcase.start_ts == testcase_result.start_ts
            assert dto_testcase.end_ts == testcase_result.end_ts

    def test_create_report_with_wrong_type(self, report):
        # given an invalid result type
        invalid_result = Mock()

        # then creating a report raises WrongReportTypeError
        with pytest.raises(WrongReportTypeError, match="Wrong report type"):
            report.create_report(invalid_result)

    def test_save_and_retrieve_report(self, report, testcase_report):
        # given a report artifact
        location = "dict://test_report.json"
        report_dict = testcase_report.to_dict(mode="json")
        report_bytes = json.dumps(report_dict).encode()

        # when artifact is saved
        report.save_artifact(location, report_bytes)

        # when retrieving the report
        retrieved_report = report.retrieve_report(location)

        # then it returns the correct report
        assert isinstance(retrieved_report, TestCaseReportDTO)
        assert retrieved_report.testcase_id == testcase_report.testcase_id

    def test_retrieve_report_with_unsupported_storage(self, report):
        # given an unsupported storage type
        location = "unsupported://test_report.json"

        # then retrieving raises StorageTypeUnknownError
        with pytest.raises(StorageTypeUnknownError, match="Storage type.*not supported"):
            report.retrieve_report(location)

    def test_retrieve_report_with_invalid_json(self, report):
        # given invalid JSON in storage
        location = "dict://test_report.json"
        report.save_artifact(location, b"invalid json")

        # then retrieving raises JSONDecodeError
        with pytest.raises(json.JSONDecodeError):
            report.retrieve_report(location)

    def test_create_artifact_without_artifact_for_testcase(self, report, testcase_report):
        # when creating an artifact for testcase report without specifying artifact
        # then it raises ReportArtifactNotSpecifiedError
        with pytest.raises(
            ReportArtifactNotSpecifiedError, match="Artifact.*must be specified"
        ):
            report.create_artifact(
                report=testcase_report,
                artifact_format=ReportArtifactFormat.JSON,
            )

    def test_create_artifact_with_wrong_report_type(self, report):
        # given an invalid report type
        invalid_report = Mock()

        # then creating an artifact raises WrongReportTypeError
        with pytest.raises(WrongReportTypeError, match="Wrong report type"):
            report.create_artifact(
                report=invalid_report,
                artifact_format=ReportArtifactFormat.JSON,
            )

    def test_create_artifact_with_no_formatter_found(self, report, testcase_report):
        # when creating an artifact with unsupported format
        # then it raises NoFormatterFoundError
        with pytest.raises(NoFormatterFoundError, match="Formatter for.*not registered"):
            report.create_artifact(
                report=testcase_report,
                artifact_format=ReportArtifactFormat.JSON,
                artifact=ReportArtifact.DIFF,  # JSON diff formatter doesn't exist
            )

    def test_save_artifact_with_unsupported_storage(self, report):
        # given an unsupported storage type
        location = "unsupported://test_artifact.txt"
        artifact_content = b"test artifact content"

        # then saving raises StorageTypeUnknownError
        with pytest.raises(StorageTypeUnknownError, match="Storage type.*not supported"):
            report.save_artifact(location, artifact_content)
