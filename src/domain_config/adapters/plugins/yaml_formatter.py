from src.domain_config.ports.plugins.i_domain_config_formatter import (
    IDomainConfigFormatter, DomainConfigFormatterError
)
import yaml  # type: ignore

class YamlFormatter(IDomainConfigFormatter):
    def deserialize(self, content: bytes) -> dict:
        try:
            return yaml.safe_load(content)
        except Exception as e:
            raise DomainConfigFormatterError(f"Failed to deserialize YAML: {e}") from e

    def serialize(self, content: dict) -> bytes:
        try:
            return yaml.safe_dump(content, allow_unicode=True).encode()
        except Exception as e:
            raise DomainConfigFormatterError(f"Failed to serialize YAML: {e}") from e
