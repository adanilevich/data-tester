import json
from typing import Dict, List
from src.report.ports import IReportFormatter, IStorage
from src.dtos import ReportArtifactDTO, TestResultDTO, ArtifactType


class Report:
    """
    Abstact report class from which TestRunReport and TestCaseReport inherit.
    Bundles common functions like creating and saving artifacts.
    """

    def __init__(self, result: TestResultDTO):
        self.result: TestResultDTO = result
        self.artifacts: Dict[str, ReportArtifactDTO] = {}

    def create_artifacts(
        self,
        formatter: IReportFormatter,
        artifact_types: List[ArtifactType],
    ):
        """
        Using provided formatter, creates a list of requested report artifacts.

        Args:
            formatter: formatter object responsible for creation of report artifacts from
                report data.
            artifact_types: List of requested artifact types
        """

        artifacts = formatter.create_artifacts(
            result=self.result,
            artifact_types=artifact_types,
        )

        for artifact in artifacts:
            if artifact is not None:
                self.artifacts[artifact.artifact_type.value] = artifact

    @staticmethod
    def save_artifacts(
        artifacts: List[ReportArtifactDTO],
        location: str,
        storage: IStorage,
        save_only_artifact_content: bool = True,
    ):
        """
        Uses storage object to save report to report storage.

        Args:
            artifacts: list of artifacts to save
            location: path (e.g. folder) where to save report to
            storage: storage adapter which stores the report, e.g. to disk or S3
            save_only_artifact_content: if True, only artifact_content will be saved
                using artifact.filename. This is typically for access by end-users,
                e.g. xlsx-based testreports. Otherwise whole artifact object will
                be serialized and saved as json - typically for caching purpose.
        """

        for artifact in artifacts:
            # if only artifact content to be save, artifact filename must be defined
            if save_only_artifact_content and artifact.filename is None:
                continue

            location = location + "/" if not location.endswith("/") else location

            if save_only_artifact_content:
                full_path = location + artifact.filename  # type: ignore
                # pydantic Base64String returns actual, unencoded string when accessing!
                content_as_str = artifact.content_b64_str
                content = content_as_str.encode()
            else:
                full_path = location + str(artifact.id) + ".json"
                content = artifact.to_json().encode()  # always store bytecontent

            storage.write(content=content, path=full_path)

    @staticmethod
    def retrieve_artifact(
        location: str,
        artifact_id: str,
        storage: IStorage,
    ) -> ReportArtifactDTO:
        """Retrieves artifact object from specified location"""

        location = location + "/" if not location.endswith("/") else location

        as_bytes: bytes = storage.read(
            path=location + artifact_id + ".json",
        )
        as_json = as_bytes.decode()

        artifact = ReportArtifactDTO.from_dict(json.loads(as_json))

        return artifact

    def to_dto(self):
        """Subclasses TestRunReport and TestCaseReport must implement this method"""
        raise NotImplementedError()
