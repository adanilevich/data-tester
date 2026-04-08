from enum import Enum


class ReportArtifactFormat(Enum):
    TXT = "txt"
    XLSX = "xlsx"


class ReportArtifact(Enum):
    REPORT = "report"
    DIFF = "diff"
