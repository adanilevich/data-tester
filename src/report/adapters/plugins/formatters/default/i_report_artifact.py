from abc import ABC, abstractmethod
import base64
from io import BytesIO
import polars as pl
import yaml #type: ignore
import json
from typing import List, Dict, Any

from src.report.adapters.plugins.formatters.default import IReportNamingConventions
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

    @classmethod
    def bytes_to_b64_string(cls, content: bytes) -> str:
        b64_str = base64.b64encode(content).decode()
        return b64_str

    @classmethod
    def b64_string_to_bytes(cls, b64_str: str) -> bytes:
        return base64.b64decode(b64_str)

    @classmethod
    def dict_to_excel_bytes(cls, data: List[Dict[str, Any]] | Dict[str, Any]) -> bytes:
        try:
            df = pl.DataFrame(data)
            excel_io = BytesIO()
            df.write_excel(excel_io)
            return excel_io.getvalue()
        except Exception as e:
            msg = f"Failed to convert dict to excel bytes: {e}"
            raise ReportArtifactError(msg) from e

    @classmethod
    def excel_bytes_to_dict(cls, excel_bytes: bytes) -> dict:
        try:
            df = pl.read_excel(excel_bytes)
            return df.to_dict(as_series=False)
        except Exception as e:
            msg = f"Failed to convert excel bytes to dict: {e}"
            raise ReportArtifactError(msg) from e

    @classmethod
    def dict_to_yaml_bytes(cls, data: dict) -> bytes:
        try:
            yaml_bytes = yaml.safe_dump(
                data=data, default_flow_style=False, indent=4, encoding="utf-8"
            )
            return yaml_bytes
        except Exception as e:
            msg = f"Failed to convert dict to yaml bytes: {e}"
            raise ReportArtifactError(msg) from e

    @classmethod
    def yaml_bytes_to_dict(cls, yaml_bytes: bytes) -> dict:
        try:
            return yaml.safe_load(yaml_bytes)
        except Exception as e:
            msg = f"Failed to convert yaml bytes to dict: {e}"
            raise ReportArtifactError(msg) from e

    @classmethod
    def json_bytes_to_dict(cls, json_bytes: bytes) -> dict:
        try:
            return json.loads(json_bytes.decode("utf-8"))
        except Exception as e:
            msg = f"Failed to convert json bytes to dict: {e}"
            raise ReportArtifactError(msg) from e
