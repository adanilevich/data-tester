import pytest
from src.domain.domain_config import (
    DomainConfig,
    DomainConfigNotUniqueError,
)
from src.dtos import DomainConfigDTO, LocationDTO
from src.infrastructure.storage.dto_storage_file import (
    JsonSerializer,
    MemoryDtoStorage,
)


class TestDomainConfig:
    @pytest.fixture
    def domain_conf(self) -> DomainConfig:
        return DomainConfig(
            storage=MemoryDtoStorage(
                serializer=JsonSerializer(),
                storage_location=LocationDTO("memory://test/"),
            )
        )

    def test_fetching_from_empty_storage(self, domain_conf: DomainConfig):
        result = domain_conf.list()
        assert len(result) == 0

    def test_matching_objects_are_fetched(
        self,
        domain_config: DomainConfigDTO,
        domain_conf: DomainConfig,
    ):
        config_a = domain_config.copy()
        config_a.domain = "a"
        config_b = domain_config.copy()
        config_b.domain = "b"

        domain_conf.save(config_a)
        domain_conf.save(config_b)

        result = domain_conf.list()
        assert len(result) == 2
        assert set(result.keys()) == {"a", "b"}

    def test_exception_if_config_already_exists(
        self,
        domain_config: DomainConfigDTO,
        domain_conf: DomainConfig,
    ):
        # Save two configs with the same domain by manipulating
        # storage internals
        config_a = domain_config.copy()
        config_a.domain = "same_domain"

        storage = domain_conf.storage
        serializer = JsonSerializer()

        # Manually write two files with same domain content but different keys
        # TODO: remove type:ignore
        content = serializer.serialize(config_a)
        with storage.fs.open(  # type: ignore
            "test/domain_configs/domain_config_dup1.json",
            "wb",
        ) as f:
            f.write(content)
        with storage.fs.open(  # type: ignore
            "test/domain_configs/domain_config_dup2.json",
            "wb",
        ) as f:
            f.write(content)

        with pytest.raises(DomainConfigNotUniqueError):
            domain_conf.list()

    def test_save_and_fetch(
        self,
        domain_config: DomainConfigDTO,
        domain_conf: DomainConfig,
    ):
        config = domain_config.copy()
        config.domain = "testdomain"

        domain_conf.save(config)

        fetched_configs = domain_conf.list()

        assert "testdomain" in fetched_configs
        fetched_config = fetched_configs["testdomain"]
        assert fetched_config.domain == config.domain
        assert fetched_config.instances == config.instances
        assert fetched_config.specifications_locations == config.specifications_locations
        assert fetched_config.testreports_location == config.testreports_location
        assert fetched_config.testcases == config.testcases

    def test_save_and_load(
        self,
        domain_config: DomainConfigDTO,
        domain_conf: DomainConfig,
    ):
        config = domain_config.copy()
        config.domain = "loadtest"

        domain_conf.save(config)
        loaded = domain_conf.load(domain="loadtest")

        assert loaded.domain == "loadtest"
        assert loaded.instances == config.instances
        assert loaded.specifications_locations == config.specifications_locations
        assert loaded.testreports_location == config.testreports_location
        assert loaded.testcases == config.testcases
