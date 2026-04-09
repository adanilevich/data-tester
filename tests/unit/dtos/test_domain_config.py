import pytest
import yaml
from src.dtos.domain_config_dtos import DomainConfigDTO
from src.dtos.storage_dtos import LocationDTO


@pytest.fixture
def domain_config() -> DomainConfigDTO:
    return DomainConfigDTO(
        domain="payments",
        instances={"test": ["alpha", "beta"], "uat": ["main"]},
        spec_locations={
            "test": ["local://specs/payments/"],
            "uat": ["local://specs/payments/uat/"],
        },
        reports_location=LocationDTO("local://reports/"),
        compare_datatypes=["int", "string", "bool"],
        sample_size_default=100,
        sample_size_per_object={},
    )


class TestDomainConfigDTO:
    def test_spec_locations_by_stage_known_stage(self, domain_config: DomainConfigDTO):
        result = domain_config.spec_locations_by_stage("test")
        assert result == [LocationDTO("local://specs/payments/")]

    def test_spec_locations_by_stage_multiple_locations(
        self, domain_config: DomainConfigDTO
    ):
        domain_config.spec_locations = {"test": ["local://a/", "local://b/"]}
        result = domain_config.spec_locations_by_stage("test")
        assert result == [LocationDTO("local://a/"), LocationDTO("local://b/")]

    def test_spec_locations_by_stage_unknown_stage(self, domain_config: DomainConfigDTO):
        with pytest.raises(KeyError):
            domain_config.spec_locations_by_stage("unknown_stage")

    def test_to_dict(self, domain_config: DomainConfigDTO):
        result = domain_config.to_dict()
        assert result["spec_locations"] == {
            "test": ["local://specs/payments/"],
            "uat": ["local://specs/payments/uat/"],
        }
        assert result["reports_location"] == LocationDTO("local://reports/").to_dict()
        assert result["compare_datatypes"] == ["int", "string", "bool"]
        assert result["sample_size_default"] == 100

    def test_to_dict_from_dict(self, domain_config: DomainConfigDTO):
        result = domain_config.to_dict()
        restored = DomainConfigDTO.from_dict(result)
        assert domain_config == restored

    def test_to_json_from_json(self, domain_config: DomainConfigDTO):
        result = domain_config.to_json()
        restored = DomainConfigDTO.from_json(result)
        assert domain_config == restored

    def test_to_yaml_from_yaml(self, domain_config: DomainConfigDTO):
        as_yaml = yaml.safe_dump(domain_config.to_dict())
        restored = DomainConfigDTO.from_dict(yaml.safe_load(as_yaml))
        assert domain_config == restored
