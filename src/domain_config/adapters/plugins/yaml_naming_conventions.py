from src.domain_config.ports.plugins.i_naming_conventions import INamingConventions
import re

class BasicYamlNamingConventions(INamingConventions):
    def match(self, name: str) -> bool:
        # Match files containing 'domain_config' not preceded by an underscore,
        # before .yaml/.yml
        match = re.match(r"^(?!_).*domain_config.*\.(yaml|yml)$", name, re.IGNORECASE)
        return bool(match)
