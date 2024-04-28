from abc import ABC, abstractmethod
from typing import Any


class DomainConfigFormatterError(Exception):
    """"""


class FormatUnknownError(DomainConfigFormatterError):
    """"""


class ContentTypeUnknownError(DomainConfigFormatterError):
    """"""


class EncodingNotSupportedError(DomainConfigFormatterError):
    """"""


class IDomainConfigFormatter(ABC):

    default_format: str  # default format of domain config, e.g. 'yaml', 'xlsx'
    default_encoding: str  # default encoding, e.g. 'utf-8'
    default_content_type: str  # defalt content type, e.g. 'application/yaml'

    @abstractmethod
    def deserialize(self, content: Any, content_type: str | None = None,
                    encoding: str | None = None) -> dict:
        """
        Parses / deserializes domain config from content assuming specified content_type.
        If content_type or encoding is not specified, default instance values are used.

        Raises:
            ContentTypeUnknownError
            DomainConfigFormatterError
        """

    @abstractmethod
    def serialize(self, content: dict, format: str | None = None,
                  encoding: str | None = None) -> Any:
        """
        Serializes a domain config (or any dictionary) to specified format using
        specified encoding. If format or encoding is not specified,
        default format and encoding are used.

        Raises:
            FormatUnknownError
            DomainConfigFormatterError
        """
