import pytest
from src.domain_config.adapters import BasicYamlNamingConventions


@pytest.mark.parametrize("name,expected", (
    ("domain_config.yaml", True),
    ("_domain_config.yaml", False),
    ("payments_domain_config_last.yaml", True),
    ("domain_info.yml", False),
    ("domain.yaml", False),
    ("domain_config.json", False),
))
def test_that_matching_names_are_recognized(name, expected):
    conventions = BasicYamlNamingConventions()

    assert conventions.match(name) is expected
