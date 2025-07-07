import pytest
import json
from src.report.adapters.plugins.formatters.default.i_report_artifact import (
    IReportArtifact, ReportArtifactError
)
from src.dtos import ArtifactType

class DummyNamingConventions:
    pass

class DummyReportArtifact(IReportArtifact):
    artifact_type = ArtifactType.JSON_TESTCASE_REPORT
    content_type = "application/octet-stream"
    sensitive = False
    def create_artifact(self, result):
        pass

def test_bytes_to_b64_and_back():
    data = b"hello world"
    b64 = IReportArtifact.bytes_to_b64_string(data)
    assert isinstance(b64, str)
    decoded = IReportArtifact.b64_string_to_bytes(b64)
    assert decoded == data

def test_dict_to_excel_and_back():
    data = {"a": [1, 2], "b": ["x", "y"]}
    excel_bytes = IReportArtifact.dict_to_excel_bytes(data)
    assert isinstance(excel_bytes, bytes)
    result = IReportArtifact.excel_bytes_to_dict(excel_bytes)
    assert result == data

def test_dict_to_yaml_and_back():
    data = {"foo": 123, "bar": [1, 2, 3]}
    yaml_bytes = IReportArtifact.dict_to_yaml_bytes(data)
    assert isinstance(yaml_bytes, bytes)
    result = IReportArtifact.yaml_bytes_to_dict(yaml_bytes)
    assert result == data

def test_json_bytes_to_dict():
    data = {"x": 1, "y": [2, 3]}
    json_bytes = json.dumps(data).encode("utf-8")
    result = IReportArtifact.json_bytes_to_dict(json_bytes)
    assert result == data

def test_dict_to_excel_bytes_error():
    # Pass a dict with lists of different lengths to trigger polars error
    with pytest.raises(ReportArtifactError):
        IReportArtifact.dict_to_excel_bytes({"a": [1, 2], "b": [3]})

def test_excel_bytes_to_dict_error():
    # Pass invalid bytes that are not a valid Excel file
    with pytest.raises(ReportArtifactError):
        IReportArtifact.excel_bytes_to_dict(b"not an excel file")

def test_dict_to_yaml_bytes_error():
    # Pass a dict with an unserializable object to trigger yaml error
    class Unserializable:
        pass
    with pytest.raises(ReportArtifactError):
        IReportArtifact.dict_to_yaml_bytes({"a": Unserializable()})

def test_yaml_bytes_to_dict_error():
    # Pass invalid YAML bytes
    with pytest.raises(ReportArtifactError):
        IReportArtifact.yaml_bytes_to_dict(b"not: [valid, yaml: }")

def test_json_bytes_to_dict_error():
    with pytest.raises(ReportArtifactError):
        IReportArtifact.json_bytes_to_dict(b"not json")
