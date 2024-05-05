import json
from typing import Dict, List
from abc import ABC, abstractmethod
import base64

from src.report.ports import IReportFormatter, IStorage
from src.dtos import ArtifactTag, ReportArtifactDTO, TestResultDTO


class Report(ABC):
    """
    Abstact report class from which TestRunReport and TestCaseReport inherit.
    Bundles common functions like creating and saving artifacts.
    """

    def __init__(self, result: TestResultDTO):
        self.result: TestResultDTO = result
        self.artifacts: Dict[str, ReportArtifactDTO]  = {}

    def create_artifacts(self, tags: List[ArtifactTag], formatter: IReportFormatter):
        """
        Using provided formatter, creates a list of report artifacts matching defined
        tags and sets self.artifacts.

        Args:
            tags: list of artifact types/tags to be created. Only artifacts which match
                one of specified tags will be created by formatter.
            formatter: formatter object responsible for creation of report artifacts from
                report data.
        """

        for artifact in formatter.format(result=self.result, tags=tags):
            self.artifacts[artifact.artifact_type.value] = artifact

    @staticmethod
    def save_artifacts(
        artifacts: List[ReportArtifactDTO],
        location: str,
        storage: IStorage,
        tags: List[ArtifactTag],
        save_only_artifact_content: bool = False,
    ):
        """
        Uses storage object to save report to report storage.

        Args:
            artifacts: list of artifacts to save
            location: path (e.g. folder) where to save report to
            tags: list of artifact tags. Only artifacts which match at least one tag
                are stored
            storage: storage adapter which stores the report, e.g. to disk or S3
            save_only_artifact_content: if True, only artifact_content will be saved
                using artifact.filename. This is typically for access by end-users,
                e.g. xlsx-based testreports. Otherwise whole artifact object will
                be serialized and saved as json - typically for caching purpose.
        """

        if len(artifacts) == 0:
            raise ValueError("Create report artifacs by formatting before storing.")

        for artifact in artifacts:

            if not Report._requested_tags_match_artifact_tags(artifact, tags):
                continue

            if save_only_artifact_content and artifact.filename is None:
                continue

            location = location + "/" if not location.endswith("/") else location

            if save_only_artifact_content:
                # if only artifact content to be save, artifact filename must be defined
                if artifact.filename is not None:
                    full_path = location + artifact.filename
                    content = Report._b64_string_to_bytes(artifact.content_b64_str)
                else:
                    continue
            else:
                full_path = location + str(artifact.id) + ".json"
                content = artifact.to_json().encode()  # always store bytecontent

            storage.write(
                content=content, content_type="application/octet-stream", path=full_path
            )

    @staticmethod
    def retrieve_artifact(
        location: str, artifact_id: str, storage: IStorage) -> ReportArtifactDTO:
        """Retrieves artifact object from specified location"""

        location = location + "/" if not location.endswith("/") else location

        as_bytes: bytes = storage.read(
            path=location + artifact_id + ".json",
            content_type="application/octet-stream",  # always read as bytes
        )
        as_json = as_bytes.decode()

        artifact = ReportArtifactDTO.from_dict(json.loads(as_json))

        return artifact

    @staticmethod
    def _b64_string_to_bytes(b64_string: str) -> bytes:
        as_b64_bytes = b64_string.encode(encoding="utf-8")
        as_bytes = base64.b64decode(as_b64_bytes)
        return as_bytes

    @staticmethod
    def _requested_tags_match_artifact_tags(
        artifact: ReportArtifactDTO,
        tags: List[ArtifactTag]
    ) -> bool:
        return any([tag in tags for tag in artifact.tags])

    @abstractmethod
    def to_dto(self):
        """Subclasses TestRunReport and TestCaseReport must implement this method"""
