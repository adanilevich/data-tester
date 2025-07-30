from src.apps.cli.domain_config_di import DomainConfigDependencyInjector
from src.domain_ports import SaveDomainConfigCommand
from src.dtos import DomainConfigDTO
from src.config import Config
from src.dtos.location import LocationDTO


class TestDomainConfigIntegration:
    def test_saving_and_fetching_config(self, domain_config: DomainConfigDTO):
        # Given: an initialized domain config manager and handler
        PATH = "dict://my/path"
        config = Config()
        config.DATATESTER_DOMAIN_CONFIGS_LOCATION = PATH
        di = DomainConfigDependencyInjector(config=config)
        manager = di.cli_domain_config_manager()
        handler = manager.domain_config_handler
        location = LocationDTO(PATH)

        # Given: two valid domain_configs to store
        domain_config_1 = domain_config.copy()
        domain_config_1.domain = "domain_1"
        domain_config_2 = domain_config.copy()
        domain_config_2.domain = "domain_2"
        domain_configs = [domain_config_1, domain_config_2]

        # When: saving the domain configs using the handler
        for dc in domain_configs:
            handler.save_domain_config(
                SaveDomainConfigCommand(config=dc, location=location)
            )

        # When: manager fetches from that location (manager uses its configured location)
        found_domain_configs = manager.fetch_domain_configs()

        # Then: two domain configs should be found
        assert len(found_domain_configs) == 2
        # Then: domain names should be domain_1 and domain_2
        domain_names = [config.domain for config in found_domain_configs.values()]
        assert "domain_1" in domain_names
        assert "domain_2" in domain_names
        dict_keys = found_domain_configs.keys()
        assert "domain_1" in dict_keys
        assert "domain_2" in dict_keys

        # When: a third domain config is saved
        domain_config_3: DomainConfigDTO = domain_config.copy()
        domain_config_3.domain = "domain_3"
        handler.save_domain_config(
            SaveDomainConfigCommand(config=domain_config_3, location=location)
        )

        # When: domain configs are searched again
        found_domain_configs = manager.fetch_domain_configs()

        # Then: 3 domain configs should be found
        assert len(found_domain_configs) == 3
