from abc import ABC, abstractmethod
from typing import List

from pydantic import Field

from src.dtos import ReportDTO, DTO, ArtifactTag


class SaveReportCommand(DTO):
    report: ReportDTO
    location: str
    tags: List[ArtifactTag]
    save_only_artifact_content: bool = Field(default=True)


class ISaveReportCommandHandler(ABC):
    @abstractmethod
    def save(self, command: SaveReportCommand):
        """Saves report to specified location"""
