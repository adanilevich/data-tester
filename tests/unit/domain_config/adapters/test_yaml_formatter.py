import pytest
from src.domain_config.adapters import YamlFormatter
from src.domain_config.ports import EncodingNotSupportedError


class TestYamlSerializer:

    formatter = YamlFormatter()

    def test_deserializing_using_default_encoding(self):

        # given a YamlFormatter
        formatter = self.formatter

        # when a yaml-formatted string is provided and no encoding specified
        content = b"'a': 1"
        dict_ = formatter.deserialize(content=content)

        # then the resulting dict is correctly parsed
        assert dict_ == {"a": 1}

    def test_that_only_utf8_encoding_is_supported_for_serialization(self):

        # given a YamlFormatter
        formatter = self.formatter

        # when a yaml-formatted string is provided and no encoding specified
        content = {"a": 1}
        encoding = "acii"
        format = "yaml"

        # then an error is raised by YamlFormatter
        with pytest.raises(EncodingNotSupportedError):
            _ = formatter.serialize(content=content, format=format, encoding=encoding)

    def test_that_dict_is_serialized_successfully(self):

        # given a YamlFormatter
        formatter = self.formatter

        # when a yaml-formatted string is provided and no encoding specified
        content = {"a": 1}
        encoding = "utf-8"
        format = "yaml"

        # then dict content is serialized as string
        result = formatter.serialize(content=content, format=format, encoding=encoding)
        assert result == "a: 1\n"
