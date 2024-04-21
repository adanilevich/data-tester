import yaml  # type: ignore

from src.domain_config.ports import ISerializer, SerializerError


class YamlSerializerError(SerializerError):
    """"""


class YamlSerializer(ISerializer):
    """
    Reads and writes yaml-based domain configs as text files.
    """

    open_mode = "r"  # will always read and write yaml as string

    def from_string(self, content: str) -> dict:
        try:
            dict_ = yaml.safe_load(content)
            return dict_
        except Exception as err:
            msg = err.__class__.__name__ + ": " + str(err)
            raise YamlSerializerError(msg)

    def from_bytes(self, content: bytes) -> dict:
        raise NotImplementedError("YamlSerializer currently only supports strings")

    def to_string(self, content: dict) -> str:
        result = yaml.safe_dump(content, default_flow_style=False)
        return result

    def to_bytes(self, content: dict) -> bytes:
        raise NotImplementedError("YamlSerializer currently only supports strings")
