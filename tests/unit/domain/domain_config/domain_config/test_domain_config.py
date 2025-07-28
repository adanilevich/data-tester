import pytest

from src.dtos import DomainConfigDTO, StorageObject
from src.dtos.location import LocationDTO
from src.domain.domain_config.core import DomainConfig, DomainConfigAlreadyExistsError
from src.infrastructure.storage.dict_storage import DictStorage
from src.infrastructure.storage.formatter_factory import FormatterFactory


class TestDomainConfig:
    @pytest.fixture
    def domain_conf(self) -> DomainConfig:
        formatter_factory = FormatterFactory()
        return DomainConfig(storage=DictStorage(formatter_factory))  # type: ignore

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

        # when these configs are saved to the storage
        domain_conf.save_config(LocationDTO("dict://"), config_a)
        domain_conf.save_config(LocationDTO("dict://"), config_b)

        # when fetching domain configs from this path
        result = domain_conf.fetch_configs(location=LocationDTO("dict://"))
        # then two domain configs are returned
        assert len(result) == 2
        assert set(result.keys()) == {"a", "b"}

    def test_exception_if_config_already_exists(
        self, domain_config: DomainConfigDTO, domain_conf: DomainConfig
    ):
        # given two domain configs with the same domain name
        config_a = domain_config.model_copy()
        config_a.domain = "same_domain"

        config_b = domain_config.model_copy()
        config_b.domain = "same_domain"

        # manually place content in storage to simulate two different files with same
        # domain - this bypasses normal save_config which would use domain as object_id
        formatter = domain_conf.storage.formatter_factory.get_formatter(  # type: ignore
            StorageObject.DOMAIN_CONFIG
        )

        # write first config with filename suffix _1
        content_a = formatter.serialize(config_a)
        domain_conf.storage._storage[  # type: ignore
            "dict://domain_config_file1.json"
        ] = content_a

        # write second config with filename suffix _2
        content_b = formatter.serialize(config_b)
        domain_conf.storage._storage[  # type: ignore
            "dict://domain_config_file2.json"
        ] = content_b

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
        assert fetched_config.testreports_location == config.testreports_location
        assert fetched_config.testcases == config.testcases
