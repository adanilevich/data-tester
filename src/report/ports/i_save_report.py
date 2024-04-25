from abc import ABC, abstractmethod
from typing import List

from pydantic import Field

from src.dtos import TestCaseReportDTO, TestRunReportDTO, DTO


class SaveReportCommand(DTO):

    report: TestRunReportDTO | TestCaseReportDTO
    location: str
    #  groub_by will store reports in subfolders of location, e.b. by date, testrun_id
    group_by: List[str] | None = Field(default=None)


class ISaveReportCommandHandler(ABC):

    @abstractmethod
    def save(self, command: SaveReportCommand):
        """Saves report to specified location"""
