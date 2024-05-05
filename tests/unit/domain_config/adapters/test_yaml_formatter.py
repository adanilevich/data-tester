from src.domain_config.adapters import YamlFormatter


class TestYamlSerializer:

    formatter = YamlFormatter()

    def test_deserializing(self):

        # given a YamlFormatter
        formatter = self.formatter

        # when a bytes object which contains a (string-transformend) dict is provided
        content = str({"a": 1}).encode()

        # then the resulting dict is correctly parsed
        dict_ = formatter.deserialize(content=content)
        assert dict_ == {"a": 1}


    def test_serializing(self):

        # given a YamlFormatter
        formatter = self.formatter

        # when a dictionary is provided
        content = {"a": 1}

        # then dict content is serialized as bytes
        result = formatter.serialize(content=content)
        assert result == b"a: 1\n"
