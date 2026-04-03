from src.apps.cli_di import CliDependencyInjector
from src.domain_ports import SaveDomainConfigCommand
from src.dtos import DomainConfigDTO
from src.config import Config


class TestDomainConfigIntegration:
    def test_saving_and_fetching_config(self, domain_config: DomainConfigDTO):
        # Given: an initialized domain config manager and handler
        config = Config()
        di = CliDependencyInjector(config=config)
        manager = di.domain_config_driver()
        handler = manager.domain_config_handler

        # Given: two valid domain_configs to store
        domain_config_1 = domain_config.copy()
        domain_config_1.domain = "domain_1"
        domain_config_2 = domain_config.copy()
        domain_config_2.domain = "domain_2"
        domain_configs = [domain_config_1, domain_config_2]

        # When: saving the domain configs using the handler
        for dc in domain_configs:
            handler.save_domain_config(SaveDomainConfigCommand(config=dc))

        # When: manager fetches configs
        found_domain_configs = manager.list_domain_configs()

        # Then: two domain configs should be found
        assert len(found_domain_configs) == 2
        domain_names = [config.domain for config in found_domain_configs.values()]
        assert "domain_1" in domain_names
        assert "domain_2" in domain_names
        dict_keys = found_domain_configs.keys()
        assert "domain_1" in dict_keys
        assert "domain_2" in dict_keys

        # When: a third domain config is saved
        domain_config_3: DomainConfigDTO = domain_config.copy()
        domain_config_3.domain = "domain_3"
        handler.save_domain_config(SaveDomainConfigCommand(config=domain_config_3))

        # When: domain configs are searched again
        found_domain_configs = manager.list_domain_configs()

        # Then: 3 domain configs should be found
        assert len(found_domain_configs) == 3

    def test_saving_and_loading_single_config(self, domain_config: DomainConfigDTO):
        config = Config()
        di = CliDependencyInjector(config=config)
        driver = di.domain_config_driver()

        # Save a domain config via the driver
        dc = domain_config.copy()
        dc.domain = "load_test_domain"
        driver.save_domain_config(config=dc)

        # Load it back via the driver
        loaded = driver.load_domain_config(domain="load_test_domain")

        assert loaded.domain == "load_test_domain"
        assert loaded.instances == dc.instances
        assert loaded.testcases == dc.testcases
