import pytest
import yaml  # type: ignore
from fsspec.implementations.memory import MemoryFileSystem  # type: ignore
from src.domain_config.dependency_injection import DomainConfigDependencyInjector
from src.dtos import DomainConfigDTO
from src.config import Config


PATH = "memory://my/path"
fs = MemoryFileSystem()


class TestDomainConfigIntegration:

    @pytest.fixture
    def persist_domain_config(self, domain_config: DomainConfigDTO):

        config_as_dict  = domain_config.to_dict()

        domain_config_1 = DomainConfigDTO.from_dict(config_as_dict)
        domain_config_1.domain = "domain_1"
        filepath_1 = PATH + "/domain_config_1.yaml"
        domain_config_2 = DomainConfigDTO.from_dict(config_as_dict)
        domain_config_2.domain = "domain_2"
        filepath_2 = PATH + "/domain_config_2.yaml"
        domain_configs = [domain_config_1, domain_config_2]
        filepaths = [filepath_1, filepath_2]

        def persist_config():

            for domain_config, filepath in zip(domain_configs, filepaths):

                domain_config_as_dict = domain_config.to_dict()

                with fs.open(filepath, "w") as file:
                    yaml.safe_dump(domain_config_as_dict, file, indent=4,
                                default_flow_style=None)

        yield persist_config

        for filepath in filepaths:
            fs.rm_file(filepath)


    def test_saving_and_fetching_config(
        self, persist_domain_config, domain_config: DomainConfigDTO):

        # given an intialized domain config manager
        di = DomainConfigDependencyInjector(config=Config())
        manager = di.domain_config_manager()

        # when a valid yaml-based domain_config is stored in a given location
        location = PATH
        persist_domain_config()

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
