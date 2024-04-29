import pytest
from pathlib import Path
from src.domain_config.di import DependencyInjector
from src.dtos import DomainConfigDTO
import yaml  # type: ignore


PATH = Path(__file__).parent.absolute()


class TestDomainConfigIntegration:

    @pytest.fixture
    def persist_domain_config(self, domain_config: DomainConfigDTO):

        filepath = PATH / "domain_config.yaml"

        def persist_config():

            domain_config_as_dict = domain_config.to_dict()

            with open(filepath, "w+") as file:
                yaml.safe_dump(domain_config_as_dict, file, indent=4,
                               default_flow_style=None)

        yield persist_config

        filepath.unlink(missing_ok=True)


    def test_fetching_config(self, persist_domain_config, domain_config: DomainConfigDTO):

        # given an intialized domain config manager
        manager = DependencyInjector().domain_config_manager()

        # when a valid yaml-based domain_config is stored in a given location
        location = "local://" + str(PATH).replace("\\", "/")
        persist_domain_config()

        # and manager fetches from that location
        found_domain_configs = manager.find(location=location)

        # then the persisted config should be found
        assert found_domain_configs[0].to_dict() == domain_config.to_dict()
