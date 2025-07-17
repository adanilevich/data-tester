import pytest
import yaml  # type: ignore

from src.dtos import DomainConfigDTO
from src.dtos.location import LocationDTO
from src.domain_config.core import DomainConfig, DomainConfigAlreadyExistsError
from src.storage.dict_storage import DictStorage


class TestDomainConfig:
    @pytest.fixture
    def domain_conf(self) -> DomainConfig:
        return DomainConfig(storage=DictStorage())  # type: ignore

    def test_fetching_from_empty_path(self, domain_conf: DomainConfig):
        # given an empty path
        empty_path = LocationDTO("dict://empty")
        # when fetching domain configs from this path
        result = domain_conf.fetch_configs(location=empty_path)
        # then result set is empty
        assert len(result) == 0

    def test_matching_objects_are_fetched(
        self, domain_config: DomainConfigDTO, domain_conf: DomainConfig
    ):
        # given two domain configs a and b with different domain names
        config_a = domain_config.model_copy()
        config_a.domain = "a"
        config_b = domain_config.model_copy()
        config_b.domain = "b"

        # when these configs and a non-config file are written to the storage
        domain_conf.storage.write(
            content=yaml.safe_dump(config_a.to_dict()).encode(),
            path=LocationDTO("dict://domain_config_a.yaml"),
        )
        domain_conf.storage.write(
            content=yaml.safe_dump(config_b.to_dict()).encode(),
            path=LocationDTO("dict://domain_config_b.yaml"),
        )
        domain_conf.storage.write(
            content=b"any text",
            path=LocationDTO("dict://not_a_config.txt"),
        )

        # when fetching domain configs from this path
        result = domain_conf.fetch_configs(location=LocationDTO("dict://"))
        # then two domain configs are returned
        assert len(result) == 2
        assert set(result.keys()) == {"a", "b"}

    def test_exception_if_config_already_exists(
        self, domain_config: DomainConfigDTO, domain_conf: DomainConfig
    ):
        # given two domain configs a and b with different domain names
        config_a = domain_config.model_copy()
        config_b = domain_config.model_copy()

        # when these configs and a non-config file are written to the storage
        domain_conf.storage.write(
            content=yaml.safe_dump(config_a.to_dict()).encode(),
            path=LocationDTO("dict://domain_config_a.yaml"),
        )
        domain_conf.storage.write(
            content=yaml.safe_dump(config_b.to_dict()).encode(),
            path=LocationDTO("dict://domain_config_b.yaml"),
        )

        with pytest.raises(DomainConfigAlreadyExistsError):
            _ = domain_conf.fetch_configs(location=LocationDTO("dict://"))

    def test_save_and_fetch(
        self, domain_config: DomainConfigDTO, domain_conf: DomainConfig
    ):
        location = LocationDTO("dict://test/location/")
        config = domain_config.model_copy()
        config.domain = "testdomain"

        # when saving config
        domain_conf.save_config(location, config)

        # then the config can be fetched back
        fetched_configs = domain_conf.fetch_configs(location)

        # and the fetched config matches the original
        assert "testdomain" in fetched_configs
        fetched_config = fetched_configs["testdomain"]
        assert fetched_config.domain == config.domain
        assert fetched_config.instances == config.instances
        assert fetched_config.specifications_locations == config.specifications_locations
        assert fetched_config.testsets_location == config.testsets_location
        assert fetched_config.testreports_location == config.testreports_location
        assert fetched_config.testcases == config.testcases
        assert fetched_config.platform_specific == config.platform_specific
