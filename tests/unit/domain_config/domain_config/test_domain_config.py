from typing import List, Any
import pytest
from src.dtos import DomainConfigDTO
from src.domain_config.ports import StorageError
from src.domain_config import DomainConfig


class DummyStorage:

    empty_path: str = "empty"
    non_existing_path: str = "non-existing"
    found_objects: List[str] = []

    def read(self, *args, **kwargs):
        return "any_value"  # value doesnt matter since serializer is mocked

    def find(self, path: str) -> List[str]:

        if path == self.non_existing_path:
            raise StorageError("My Exception")
        elif path == self.empty_path:
            return []
        else:
            return self.found_objects


class DummyNamingConventions:

    matching_string: str = "match"

    def match(self, name: str) -> bool:
        return True if self.matching_string in name else False


class DummyFormatter:

    return_value: Any = None
    default_content_type: str = "doesnt matter"
    default_format: str = "doesnt matter"
    default_encoding: str = "doesnt matter"

    def deserialize(self, *args, **kwargs) -> dict:
        return self.return_value


class TestDomainConfigManager:

    @pytest.fixture
    def manager(self, domain_config: DomainConfigDTO) -> DomainConfig:

        formatter = DummyFormatter()
        formatter.return_value = domain_config.to_dict()

        manager = DomainConfig(
            naming_conventions=DummyNamingConventions(),  # type: ignore
            formatter=formatter,  # type: ignore
            storage=DummyStorage(),  # type: ignore
        )

        return manager

    def test_fetching_from_empy_path_returns_empty_list(
            self, manager: DomainConfig):

        # given an empty path is specified
        path = "empty"
        manager.storage.empty_path = path  # type: ignore

        # when fetching domain configs from this path
        result = set(
            str(conf.to_dict())  # convert to string for to make it hasheable
            for conf in manager.fetch_configs(location=path)
        )

        # then result set is empty
        assert result == set([])

    def test_fetching_from_non_existing_path_returns_empty_list(
            self, manager: DomainConfig):

        # given a non-existing path is defined
        path = "non-existing"
        manager.storage.non_existing_path = path  # type: ignore

        # when fetching domain configs from this path
        result = set(
            str(conf.to_dict())  # convert to string for to make it hasheable
            for conf in manager.fetch_configs(location=path)
        )

        # then result set is empty
        assert result == set([])

    def test_fetch_only_accepts_string_inputs(self, manager: DomainConfig):

        # given a non-string-valued path is defined
        path = 1

        # then fetching domain configs from this path results in an error
        with pytest.raises(ValueError):
            _ = manager.fetch_configs(location=path)  # type: ignore

    def test_matching_objects_are_fetched(
            self, manager: DomainConfig, domain_config: DomainConfigDTO):

        # given a patch where matching and non-matching objects are stored
        path = "good_path"
        found_objects = ["match1", "match2", "bad"]
        manager.storage.found_objects = found_objects  # type: ignore
        manager.naming_conventions.matching_string = "match"  # type: ignore
        manager.formatter.return_value = domain_config.to_dict()  # type: ignore

        # when fetching domain configs from this path
        result = set(
            str(conf.to_dict())  # convert to string for to make it hasheable
            for conf in manager.fetch_configs(location=path)
        )

        # then a domain config is returned for each object matching naming conventions
        expected = set(
            str(domain_config.to_dict())  # convert to string for to make it hasheable
            for _ in range(2)
        )
        assert result == expected
