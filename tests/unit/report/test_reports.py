import json
from typing import Dict, List
from uuid import uuid4
import base64
from datetime import datetime
import pytest
from src.report import Report, TestCaseReport, TestRunReport
from src.dtos import (
    ReportArtifactDTO, ArtifactType, TestResult, TestResultDTO,
    TestCaseResultDTO, TestRunResultDTO, TestCaseReportDTO, TestRunReportDTO
)
from src.report.ports import IReportFormatter, IStorage


class DictStorage(IStorage):

    store: Dict[str, bytes] = {}

    def read(self, path: str) -> bytes:
        return self.store[path]

    def write(self, content: bytes, path: str):
        self.store[path] = content


def string_2_b64string(input: str) -> str:
    as_bytes = input.encode()
    as_b64_bytes = base64.b64encode(as_bytes)
    as_b64_string = as_b64_bytes.decode()
    return as_b64_string

artifact = ReportArtifactDTO(
            id=uuid4(),
            artifact_type=ArtifactType.TXT_TESTCASE_REPORT,
            sensitive=False,
            content_type="plain/text",
            content_b64_str=string_2_b64string("my_content"),
            filename="dummy_report.txt",
            testrun_id=uuid4(),
            start_ts=datetime.now(),
            result=TestResult.OK,
        )

class DummyFormatter(IReportFormatter):

    artifacts: List[ReportArtifactDTO]

    def __init__(self, artifacts: List[ReportArtifactDTO] | None = None):
        self.artifacts = artifacts or []

    def create_artifacts(
        self,
        result: TestResultDTO,
        artifact_types: List[ArtifactType]
    ) -> List[ReportArtifactDTO]:
        self.result = result
        self.artifact_types = artifact_types
        return [art for art in self.artifacts if art.artifact_type in artifact_types]


class TestReport:

    @pytest.fixture
    def report(self, testcase_result) -> Report:
        return Report(result=testcase_result)

    def test_creating_artifacts(self, report: Report):
        # given a Report and a ReportFormatter
        report = report
        formatter = DummyFormatter()

        # when formatter returns two different report artifacts
        artifact_1 = artifact.create_copy()
        artifact_1.artifact_type = ArtifactType.TXT_TESTCASE_REPORT
        artifact_2 = artifact.create_copy()
        artifact_2.artifact_type = ArtifactType.JSON_TESTCASE_REPORT
        formatter.artifacts = [artifact_1, artifact_2]

        # and both artifact types are requested
        requested_artifact_types = [
            ArtifactType.JSON_TESTCASE_REPORT, ArtifactType.TXT_TESTCASE_REPORT
        ]

        # then creating artifacts updates report.artifacts with both artifacts
        report.create_artifacts(
            artifact_types=requested_artifact_types,
            formatter=formatter
        )  # type: ignore
        assert report.artifacts == {
            "txt-testcase-report": artifact_1,
            "json-testcase-report": artifact_2
        }

    def test_only_requested_artifact_types_are_created(self, report: Report):
        # given a Report and a Storage
        report = report
        formatter = DummyFormatter()

        # when formatter returns two different report artifacts
        artifact_1 = artifact.create_copy()
        artifact_1.artifact_type = ArtifactType.TXT_TESTCASE_REPORT
        artifact_2 = artifact.create_copy()
        artifact_2.artifact_type = ArtifactType.JSON_TESTCASE_REPORT
        formatter.artifacts = [artifact_1, artifact_2]

        # and only one artifact type is requested
        requested_artifact_types = [ArtifactType.JSON_TESTCASE_REPORT]

        # then creating artifacts updates report.artifacts with both artifacts
        report.create_artifacts(
            artifact_types=requested_artifact_types,
            formatter=formatter
        )  # type: ignore
        assert report.artifacts == {"json-testcase-report": artifact_2}

    def test_saving_whole_artifact_objects_works(self, report: Report):
        # given a Report and a Storage
        report = report
        storage = DictStorage()

        # when an artifact is to be saved as whole object
        artifact_1 = artifact.create_copy()
        store_only_artifact_content = False

        # then whole artifact object is saved as "artifact_id.json"
        report.save_artifacts(
            artifacts=[artifact_1],
            location="artifacts/",
            save_only_artifact_content=store_only_artifact_content,
            storage=storage
        )
        artifact_as_bytes = storage.store[f"artifacts/{artifact_1.id}.json"]
        artifact_as_string = artifact_as_bytes.decode()
        artifact_as_dict= json.loads(artifact_as_string)
        artifact_as_object = ReportArtifactDTO.from_dict(artifact_as_dict)
        assert artifact_as_object == artifact_1

    def test_that_retrieving_artifacts_works(self, report: Report):
        # given a Report and a Storage
        report = report
        storage = DictStorage()

        # when an artifact is saved
        artifact_1 = artifact.create_copy()
        store_only_artifact_content = False
        report.save_artifacts(
            artifacts=[artifact_1],
            location="artifacts/",
            save_only_artifact_content=store_only_artifact_content,
            storage=storage
        )

        # then this artifact can be retrieved by its artifact_id
        result = report.retrieve_artifact(
            artifact_id=str(artifact_1.id),
            location="artifacts/",
            storage=storage,
        )
        assert result == artifact_1


class TestTestCaseReport:

    def test_converting_to_dto(self, testcase_result: TestCaseResultDTO):
        # given a testcase report incl. artifacts
        report = TestCaseReport(result=testcase_result)
        report.artifacts = {artifact.artifact_type.value: artifact}

        # then it is successfully transformed to a DTO
        report_dto = report.to_dto()
        assert isinstance(report_dto, TestCaseReportDTO)
        assert report_dto.artifacts == report.artifacts


class TestTestRunReport:
    def test_converting_to_dto(self, testrun_result: TestRunResultDTO):
        # given a testcase report incl. artifacts
        report = TestRunReport(result=testrun_result)
        report.artifacts = {artifact.artifact_type.value: artifact}

        # then it is successfully transformed to a DTO
        report_dto = report.to_dto()
        assert isinstance(report_dto, TestRunReportDTO)
        assert report_dto.artifacts == report.artifacts
