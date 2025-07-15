import pytest
import yaml  # type: ignore

from src.dtos.domain_config import DomainConfigDTO
from src.dtos.location import LocationDTO


class TestDomainConfigDTO:

    def test_getting_specifications_location_when_string_valued(
            self, domain_config: DomainConfigDTO):

        for locations in [
            LocationDTO("local://here"),
            [LocationDTO("local://there"), LocationDTO("local://anywhere")]
        ]:
            domain_config.specifications_locations = locations  # type: ignore

            result = domain_config.specifications_locations_by_instance("stage", "inst")
            assert result == locations if isinstance(locations, list) else [locations]

    def test_getting_specifications_location_when_dict_valued(
            self, domain_config: DomainConfigDTO):

        locations = {
            "uat.main": [LocationDTO("local://here")],
            "test.alpha": [LocationDTO("local://there")],
        }
        domain_config.specifications_locations = locations  # type: ignore
        for stage, instance in [("uat", "main"), ("test", "alpha")]:
            result = domain_config.specifications_locations_by_instance(stage, instance)
            expected = locations[f"{stage}.{instance}"]
            assert result == expected if isinstance(expected, list) else [expected]

        with pytest.raises(KeyError):
            _ = domain_config.specifications_locations_by_instance("unknown", "inst")

    def test_to_dict(self, domain_config: DomainConfigDTO):
        domain_config.specifications_locations = [
            LocationDTO("local://here")]  # type: ignore
        result = domain_config.to_dict()
        expected = result["specifications_locations"]
        assert expected == [LocationDTO("local://here").to_dict()]

    def test_to_dict_from_dict(self, domain_config: DomainConfigDTO):
        domain_config.specifications_locations = [
            LocationDTO("local://here")]  # type: ignore
        result = domain_config.to_dict()
        new_domain_config = DomainConfigDTO.from_dict(result)
        assert domain_config == new_domain_config

    def test_to_json_from_json(self, domain_config: DomainConfigDTO):
        domain_config.specifications_locations = [
            LocationDTO("local://here")]  # type: ignore
        result = domain_config.to_json()
        new_domain_config = DomainConfigDTO.from_json(result)
        assert domain_config == new_domain_config

    def test_to_yaml_from_yaml(self, domain_config: DomainConfigDTO):
        domain_config.specifications_locations = [
            LocationDTO("local://here")]  # type: ignore
        result = domain_config
        as_yaml = yaml.safe_dump(result.to_dict())
        new_domain_config = DomainConfigDTO.from_dict(yaml.safe_load(as_yaml))
        assert domain_config == new_domain_config
