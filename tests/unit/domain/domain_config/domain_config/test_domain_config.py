import pytest

from src.dtos import DomainConfigDTO, LocationDTO
from src.domain.domain_config import (
    DomainConfig,
    DomainConfigAlreadyExistsError,
)
from src.infrastructure.storage.dto_storage_file import (
    MemoryDtoStorage,
)
from src.infrastructure.storage.dto_storage_file import JsonSerializer


class TestDomainConfig:
    @pytest.fixture
    def domain_conf(self) -> DomainConfig:
        return DomainConfig(
            storage=MemoryDtoStorage(
                serializer=JsonSerializer(),
                storage_location=LocationDTO("memory://test/"),
            )
        )

    def test_fetching_from_empty_storage(
        self, domain_conf: DomainConfig
    ):
        result = domain_conf.fetch_configs()
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

        domain_conf.save_config(config_a)
        domain_conf.save_config(config_b)

        result = domain_conf.fetch_configs()
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

        with pytest.raises(DomainConfigAlreadyExistsError):
            domain_conf.fetch_configs()

    def test_save_and_fetch(
        self,
        domain_config: DomainConfigDTO,
        domain_conf: DomainConfig,
    ):
        config = domain_config.copy()
        config.domain = "testdomain"

        domain_conf.save_config(config)

        fetched_configs = domain_conf.fetch_configs()

        assert "testdomain" in fetched_configs
        fetched_config = fetched_configs["testdomain"]
        assert fetched_config.domain == config.domain
        assert fetched_config.instances == config.instances
        assert (
            fetched_config.specifications_locations
            == config.specifications_locations
        )
        assert (
            fetched_config.testreports_location
            == config.testreports_location
        )
        assert fetched_config.testcases == config.testcases
