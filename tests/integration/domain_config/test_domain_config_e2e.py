from src.domain_config.dependency_injection import DomainConfigDependencyInjector
from src.dtos import DomainConfigDTO
from src.config import Config
from src.dtos.location import LocationDTO


class TestDomainConfigIntegration:

    def test_saving_and_fetching_config(self, domain_config: DomainConfigDTO):

        # given an intialized domain config manager
        PATH = "dict://my/path"
        config = Config()
        config.DATATESTER_DOMAIN_CONFIGS_LOCATION = PATH
        di = DomainConfigDependencyInjector(config=config)
        manager = di.domain_config_manager()

        # when valid yaml-based domain_configs are stored in a given location
        location = LocationDTO(PATH)

        domain_config_1 = domain_config.model_copy()
        domain_config_1.domain = "domain_1"
        domain_config_2 = domain_config.model_copy()
        domain_config_2.domain = "domain_2"
        domain_configs = [domain_config_1, domain_config_2]

        for domain_config in domain_configs:
            manager.save_domain_config(location=location, config=domain_config)

        # and manager fetches from that location
        found_domain_configs = manager.fetch_domain_configs(location=location)

        # then two domain configs should be found
        assert len(found_domain_configs) == 2

        # and domain names should be domain_1 and domain_2
        domain_names = [config.domain for config in found_domain_configs.values()]
        assert "domain_1" in domain_names
        assert "domain_2" in domain_names

        dict_keys = found_domain_configs.keys()
        assert "domain_1" in dict_keys
        assert "domain_2" in dict_keys

        # and when a third domain config is saved
        domain_config_3: DomainConfigDTO = domain_config.model_copy()
        domain_config_3.domain = "domain_3"
        manager.save_domain_config(location=location, config=domain_config_3)

        # and domain configs are searched again
        found_domain_configs = manager.fetch_domain_configs(location=location)

        # then 3 domain configs should be found
        assert len(found_domain_configs) == 3
