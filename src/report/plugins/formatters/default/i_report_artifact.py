from abc import ABC, abstractmethod
from base64 import b64encode

from src.report.plugins.formatters.default import IReportNamingConventions
from src.dtos import TestResultDTO, ReportArtifactDTO, ArtifactType


class ReportArtifactError(Exception):
    """"""


class ResultTypeNotSupportedError(ReportArtifactError):
    """"""


class IReportArtifact(ABC):

    artifact_type: ArtifactType
    content_type: str
    sensitive: bool
    naming_conventions: IReportNamingConventions

    def __init__(self, naming_conventions: IReportNamingConventions):
        self.naming_conventions: IReportNamingConventions = naming_conventions

    @abstractmethod
    def create_artifact(self, result: TestResultDTO) -> ReportArtifactDTO:
        """Abstract class for format-specific formatters"""

    @staticmethod
    def bytes_to_b64_string(content: bytes) -> str:
        return b64encode(content).decode()
