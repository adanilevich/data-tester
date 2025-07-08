import os
import pytest
from src.domain_config.ports import FetchDomainConfigsCommand
from src.domain_config.drivers import DomainConfigManager
from src.config import Config


class DummyFetchDomainConfigsCommandHandler:

    def fetch(self, command: FetchDomainConfigsCommand):
        if "exception" in command.location:
            raise ValueError("Dummy Error")

        return command


class TestSimpleDomainConfigManager:

    manager = DomainConfigManager(
        fetch_command_handler=DummyFetchDomainConfigsCommandHandler(),  # type: ignore
        config=Config()
    )

    @pytest.fixture
    def set_env(self):
        os.environ["DATATESTER_DOMAIN_CONFIGS_LOCATION"] = "a"
        yield
        del os.environ["DATATESTER_DOMAIN_CONFIGS_LOCATION"]

    def test_that_location_is_searched_if_defined(self):
        result = self.manager.fetch_domain_configs(location="a")
        assert result == FetchDomainConfigsCommand(location="a")

    def test_that_fetch_exceptions_lead_to_empty_return(self):
        result = self.manager.fetch_domain_configs("exception")
        assert result == {}

    def test_fallback_to_location_from_envs(self, set_env):
        # have to explicitely instantiate a config such that it reads from envs which
        # are set by the fixture set_env
        config = Config()
        manager = DomainConfigManager(
            fetch_command_handler=DummyFetchDomainConfigsCommandHandler(),  # type: ignore
            config=config
        )
        result = manager.fetch_domain_configs()

        assert result == FetchDomainConfigsCommand(location="a")

    def test_exception_is_raised_if_no_locations_defined(self):
        with pytest.raises(ValueError):
            _ = self.manager.fetch_domain_configs()
