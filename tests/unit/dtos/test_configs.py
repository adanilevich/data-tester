import pytest
from src.dtos.domain_config import DomainConfigDTO


class TestDomainConfigDTO:

    def test_getting_string_valued_testmatrix_location(
            self, domain_config: DomainConfigDTO):

        domain_config.testmatrices_locations = "this_location"

        for stage, instance in [("any", "value"), ("doesnt", "matter")]:
            result = domain_config.testmatrix_location_by_instance(stage, instance)
            assert result == "this_location"

    def test_getting_testmatrix_location_by_stage(
            self, domain_config: DomainConfigDTO):
        domain_config.testmatrices_locations = {"uat.main": "here", "test.alpha": "there"}

        result = domain_config.testmatrix_location_by_instance("uat", "main")
        assert result == "here"

        with pytest.raises(KeyError):
            _ = domain_config.testmatrix_location_by_instance("unknown", "instance")

    def test_getting_specifications_location_when_string_valued(
            self, domain_config: DomainConfigDTO):

        for locations in ["here", ["there", "anywhere"]]:
            domain_config.specifications_locations = locations  # type: ignore

            result = domain_config.specifications_locations_by_instance("stage", "inst")
            assert result == locations if isinstance(locations, list) else [locations]

    def test_getting_specifications_location_when_dict_valued(
            self, domain_config: DomainConfigDTO):

        locations = {"uat.main": ["here"], "test.alpha": "there"}
        domain_config.specifications_locations = locations  # type: ignore
        for stage, instance in [("uat", "main"), ("test", "alpha")]:
            result = domain_config.specifications_locations_by_instance(stage, instance)
            expected = locations[f"{stage}.{instance}"]
            assert result == expected if isinstance(expected, list) else [expected]

        with pytest.raises(KeyError):
            _ = domain_config.specifications_locations_by_instance("unknown", "inst")
