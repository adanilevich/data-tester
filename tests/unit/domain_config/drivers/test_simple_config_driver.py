import os
import pytest
from src.domain_config.drivers import SimpleConfigFinder
from src.domain_config.ports import FetchDomainConfigsCommand


class DummyFetchDomainConfigsCommandHandler:

    def fetch(self, command):
        if any(["exception" in loc for loc in command.locations]):
            raise ValueError("Dummy Error")

        return command


class TestSimpleConfigFinder:

    @pytest.fixture
    def handler(self) -> DummyFetchDomainConfigsCommandHandler:
        return DummyFetchDomainConfigsCommandHandler()

    @pytest.fixture
    def set_env_multiple_configs(self):
        locations = ["a", "b"]
        os.environ["DATATESTER_DOMAIN_CONFIG_LOCATIONS"] = ",".join(locations)
        yield
        del os.environ["DATATESTER_DOMAIN_CONFIG_LOCATIONS"]

    @pytest.fixture
    def set_env_one_config(self):
        os.environ["DATATESTER_DOMAIN_CONFIG_LOCATION"] = "a "
        yield
        del os.environ["DATATESTER_DOMAIN_CONFIG_LOCATION"]

    def test_that_provided_commands_are_handled(self, handler):

        finder = SimpleConfigFinder(handler)
        commands = ["a", "b"]

        result = finder.find(commands)

        assert result == FetchDomainConfigsCommand(locations=commands)

    def test_that_fetch_exceptions_lead_to_empty_return(self, handler):

        finder = SimpleConfigFinder(handler)
        commands = ["a", "exception"]

        result = finder.find(commands)

        assert result == []

    def test_fallback_to_locations_from_envs(self, handler, set_env_multiple_configs):

        finder = SimpleConfigFinder(handler)

        result = finder.find()

        assert result == FetchDomainConfigsCommand(locations=["a", "b"])

    def test_fallback_to_one_location_from_envs(self, handler, set_env_one_config):

        finder = SimpleConfigFinder(handler)

        result = finder.find()

        assert result == FetchDomainConfigsCommand(locations=["a"])

    def test_excetion_is_raised_if_no_locations_defined(self, handler):

        finder = SimpleConfigFinder(handler)

        with pytest.raises(ValueError):
            _ = finder.find()
