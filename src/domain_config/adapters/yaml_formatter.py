import yaml  # type: ignore

from src.domain_config.ports import IDomainConfigFormatter, DomainConfigFormatterError


class YamlFormatter(IDomainConfigFormatter):
    """
    Reads and writes yaml-based domain configs as text files.
    """

    default_format: str = "yaml"
    default_encoding: str = "utf-8"

    def deserialize(self, content: bytes) -> dict:
        """Loads yaml file from bytecontent"""
        try:
            return yaml.safe_load(content)  # encoding is inferred by pyyaml
        except Exception as err:
            msg = err.__class__.__name__ + ": " + str(err)
            raise DomainConfigFormatterError(msg) from err

    def serialize(self, content: dict) -> bytes:
        """Serializes a dictionary to yamlfile and returns bytecontent of file."""

        # yaml.dump produces a byte-like object if encoding is specified.
        result = yaml.safe_dump(
            data=content,
            encoding=self.default_encoding,
            default_flow_style=False,
            indent=4,
        )

        return result
