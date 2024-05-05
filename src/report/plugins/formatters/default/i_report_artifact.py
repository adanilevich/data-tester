from abc import ABC, abstractmethod

from src.report.plugins.formatters.default import IReportNamingConventions
from src.dtos import TestResultDTO, ReportArtifactDTO


class IReportArtifact(ABC):

    artifact_type: str
    content_type: str
    naming_conventions: IReportNamingConventions

    def __init__(self, naming_conventions: IReportNamingConventions):
        self.naming_conventions: IReportNamingConventions = naming_conventions

    @abstractmethod
    def format(self, result: TestResultDTO) -> ReportArtifactDTO:
        """Abstract class for format-specific formatters"""
