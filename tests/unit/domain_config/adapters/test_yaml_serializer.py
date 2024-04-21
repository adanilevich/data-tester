import pytest
from src.domain_config.adapters import YamlSerializer, YamlSerializerError


class TestYamlSerializer:

    serializer = YamlSerializer()

    def test_reading_from_bytes_not_implemented(self):
        with pytest.raises(NotImplementedError):
            _ = self.serializer.from_bytes(b"'a': 1")

    def test_writing_as_bytes_not_implemented(self):
        with pytest.raises(NotImplementedError):
            _ = self.serializer.to_bytes({"a": 1})

    def test_error_when_reading_from_bad_string(self):
        with pytest.raises(YamlSerializerError):
            _ = self.serializer.from_string(1233132)  # type: ignore

    def test_reading_yaml_from_string(self):
        assert self.serializer.from_string("'a': 1") == {"a": 1}
        assert self.serializer.from_string("a: 1") == {"a": 1}

    def test_writing_yaml_to_string(self):
        assert self.serializer.to_string({"a": True}) == "a: true\n"
