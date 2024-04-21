from src.domain_config.ports import INamingConventions


class BasicYamlNamingConventions(INamingConventions):
    """Matches all strings which end with .yaml or .yaml and contanin 'config'"""

    def match(self, name: str) -> bool:
        if all([
            name.endswith((".yaml", "yml")),
            "domain_config" in name,
            not name.startswith("_"),
        ]):
            return True
        else:
            return False
