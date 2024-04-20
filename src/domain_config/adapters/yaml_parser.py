import yaml  # type: ignore

from src.domain_config.ports import IParser


class YamlParser(IParser):

    def parse(self, content: bytes | str) -> dict:
        try:
            dict_ = yaml.safe_load(content)
            return dict_
        except yaml.YAMLError:
            return {}
