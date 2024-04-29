from typing import Any
import yaml  # type: ignore

from src.domain_config.ports import (
    IDomainConfigFormatter, DomainConfigFormatterError, FormatUnknownError,
    EncodingNotSupportedError
)


class YamlFormatter(IDomainConfigFormatter):
    """
    Reads and writes yaml-based domain configs as text files.
    """

    default_format: str = "yaml"
    default_encoding: str = "utf-8"
    default_content_type: str = "application/yaml"

    def deserialize(self, content: Any, content_type: str | None = None,
                    encoding: str | None = None) -> dict:

        try:
            return yaml.safe_load(content)  # encoding is inferred by pyyaml
        except Exception as err:
            msg = err.__class__.__name__ + ": " + str(err)
            raise DomainConfigFormatterError(msg) from err

    def serialize(self, content: dict, format: str | None = None,
                  encoding: str | None = None) -> Any:

        encoding = encoding or self.default_encoding
        if encoding not in ["utf-8", "unicode"]:
            msg = "YamlFormatter only supports 'utf-8' and 'unicode' encoding."
            raise EncodingNotSupportedError(msg)

        if format != self.default_format:
            msg = f"YamlFormatter only supports yaml as format, not {format}"
            raise FormatUnknownError(msg)

        # yaml.dump produces a byte-like object if encoding is specified. Should be
        # string for compatibility with FileStorage.write()
        result = yaml.safe_dump(
            data=content, encoding=encoding, default_flow_style=False).decode(encoding)

        return result
