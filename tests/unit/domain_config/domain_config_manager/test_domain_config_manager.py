from typing import List
import pytest
from src.dtos import DomainConfigDTO
from src.domain_config.ports import StorageError
from src.domain_config import DomainConfigManager


found_objects = ["good_object_1", "good_object_2", "bad_object_1"]


class DummyStorage:

    def read_text(self, *args, **kwargs):
        return "my_text"

    def read_bytes(self, *args, **kwargs):
        return b"my_text"

    def find(self, path: str) -> List[str]:
        if "good" in path:
            return found_objects
        elif "exception" in path:
            raise StorageError("My Exception")
        else:
            return []


class DummyNamingConventions:

    def match(self, name: str) -> bool:
        return True if "good" in name else False


class DummySerializer:

    open_mode: str = "r"

    def __init__(self, return_val):
        self.return_val = return_val

    def from_string(self, content: str) -> dict:
        return self.return_val


class TestDomainConfigManager:

    @pytest.fixture
    def setup(self, domain_config: DomainConfigDTO):
        self.serializer = DummySerializer(return_val=domain_config.to_dict())
        self.manager = DomainConfigManager(
            naming_conventions=DummyNamingConventions(),  # type: ignore
            serializer=self.serializer,  # type: ignore
            storage=DummyStorage(),  # type: ignore
        )

    @pytest.mark.parametrize("location", (
        "good",
        "bad",
        "exception",
    ))
    def test_fetching_specs(self, setup, domain_config, location):

        result = set(
            str(conf.to_dict())  # convert to string for to make it hasheable
            for conf in self.manager.fetch_configs(location)
        )

        if location == "good":
            expected = set(
                str(conf.to_dict())
                for conf in [domain_config, domain_config]
            )
        else:
            expected = set([])

        assert result == expected

    def test_fetch_only_accepts_string_inputs(self, setup):
        with pytest.raises(ValueError):
            _ = self.manager.fetch_configs(["safasdf"])  # type: ignore
