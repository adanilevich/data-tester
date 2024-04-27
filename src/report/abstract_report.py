from typing import Any, List
from abc import ABC, abstractmethod

from src.report.ports import IReportFormatter, IStorage, IReportNamingConventions


class AbstractReport(ABC):

    def __init__(self, format: str | None = None, content_type: str | None = None,
                 content: Any = None):

        self.format = format
        self.content_type = content_type
        self.content = content

    def format_report(self, format: str, formatter: IReportFormatter):

        _ = formatter.format(report=self, format=format)

        return self.to_dto()

    def save_report(self, location, group_by: List[str],
                    naming_conventions: IReportNamingConventions, storage: IStorage):

        if self.format_report is None:
            raise ValueError("Report must be formatted and the applied format specified.")

        if self.content_type is None:
            raise ValueError("Content type of report to be saved must be defined!")

        if group_by is not None:
            for item in group_by:
                if item in self.to_dto().model_fields:
                    location += item + "/"

        filename = location + "/" + naming_conventions.report_name(self.to_dto())

        storage.save(
            content=self.content,
            content_type=self.content_type,
            location=filename
        )

    @abstractmethod
    def to_dto(self):
        """"""
