import os
import pytest
from src.domain_config.ports import (
    FetchDomainConfigsCommand, SaveDomainConfigCommand, IDomainConfigHandler
)
from src.domain_config.drivers.cli_domain_config_manager import CLIDomainConfigManager
from src.config import Config
from src.dtos.location import LocationDTO

class DummyDomainConfigHandler(IDomainConfigHandler):
    def fetch_domain_configs(self, command: FetchDomainConfigsCommand):
        if "exception" in command.location.path:
            raise ValueError("Dummy Error")
        return command
    def save_domain_config(self, command: SaveDomainConfigCommand):
        pass

class TestSimpleCLIDomainConfigManager:
    manager = CLIDomainConfigManager(
        domain_config_handler=DummyDomainConfigHandler(),  # type: ignore
        config=Config()
    )

    @pytest.fixture
    def set_env(self):
        os.environ["DATATESTER_DOMAIN_CONFIGS_LOCATION"] = "dict://a"
        yield
        del os.environ["DATATESTER_DOMAIN_CONFIGS_LOCATION"]

    def test_that_location_is_searched_if_defined(self):
        result = self.manager.fetch_domain_configs(
            location=LocationDTO("dict://a")
        )
        assert result == FetchDomainConfigsCommand(location=LocationDTO("dict://a"))

    def test_that_fetch_exceptions_lead_to_empty_return(self):
        result = self.manager.fetch_domain_configs(
            LocationDTO("dict://exception")
        )
        assert result == {}

    def test_fallback_to_location_from_envs(self, set_env):
        config = Config()
        manager = CLIDomainConfigManager(
            domain_config_handler=DummyDomainConfigHandler(),  # type: ignore
            config=config
        )
        result = manager.fetch_domain_configs()
        assert result == FetchDomainConfigsCommand(location=LocationDTO("dict://a"))

    def test_exception_is_raised_if_no_locations_defined(self):
        with pytest.raises(ValueError):
            _ = self.manager.fetch_domain_configs()
