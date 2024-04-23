import os
import pytest
from src.domain_config.drivers import SimpleConfigManager
from src.domain_config.ports import FetchDomainConfigsCommand


class DummyFetchDomainConfigsCommandHandler:

    def fetch(self, command: FetchDomainConfigsCommand):
        if "exception" in command.location:
            raise ValueError("Dummy Error")

        return command


class TestSimpleConfigFinder:

    @pytest.fixture
    def manager(self) -> SimpleConfigManager:
        return SimpleConfigManager(
            handler=DummyFetchDomainConfigsCommandHandler()  # type: ignore
        )

    @pytest.fixture
    def set_env(self):
        os.environ["DATATESTER_DOMAIN_CONFIGS_LOCATION"] = "a "
        yield
        del os.environ["DATATESTER_DOMAIN_CONFIGS_LOCATION"]

    def test_that_location_is_searched_if_defined(self, manager):

        result = manager.find(location="a")

        assert result == FetchDomainConfigsCommand(location="a")

    def test_that_fetch_exceptions_lead_to_empty_return(self, manager):

        result = manager.find("exception")

        assert result == []

    def test_fallback_to_location_from_envs(self, manager, set_env):

        result = manager.find()

        assert result == FetchDomainConfigsCommand(location="a")

    def test_excetion_is_raised_if_no_locations_defined(self, manager):

        with pytest.raises(ValueError):
            _ = manager.find()
