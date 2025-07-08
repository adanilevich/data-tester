from typing import List
import pytest
from src.dtos import DomainConfigDTO
from src.domain_config.ports import StorageError
from src.domain_config.core import DomainConfig, DomainConfigAlreadyExistsError
import yaml  # type: ignore

class DummyStorage:
    empty_path: str = "empty"
    non_existing_path: str = "non-existing"
    found_objects: List[str] = []
    file_contents: dict = {}
    written_files: dict = {}

    def read(self, path: str, *args, **kwargs):
        if path in self.file_contents:  # type: ignore
            return self.file_contents[path]  # type: ignore
        return b""

    def find(self, path: str) -> List[str]:
        if path == self.non_existing_path:
            raise StorageError("My Exception")
        elif path == self.empty_path:
            return []
        else:
            return self.found_objects

    def write(self, content: bytes, path: str):
        self.written_files[path] = content

class TestDomainConfig:
    domain_config:DomainConfig = DomainConfig(storage=DummyStorage())  # type: ignore

    def test_fetching_from_empty_path_returns_empty_list(self):
        # given an empty path
        empty_path = DummyStorage.empty_path
        # when fetching domain configs from this path
        result = self.domain_config.fetch_configs(location=empty_path)
        # then result set is empty
        assert len(result) == 0

    def test_fetching_from_non_existing_path_returns_empty_list(self):
        # given a non-existing path
        non_existing_path = DummyStorage.non_existing_path
        # when fetching domain configs from this path
        result = self.domain_config.fetch_configs(location=non_existing_path)
        # then result set is empty
        assert len(result) == 0

    def test_fetch_only_accepts_string_inputs(self):
        path = 1
        with pytest.raises(ValueError):
            _ = self.domain_config.fetch_configs(location=path)  # type: ignore

    def test_matching_objects_are_fetched(self, domain_config: DomainConfigDTO):
        # given a path with matching and non-matching objects
        path = "good_path"
        matching_files = [
            "domain_config_a.yaml", "domain_config_b.yaml", "not_a_config.txt"]
        self.domain_config.storage.found_objects = matching_files  # type: ignore
        # and given two domain configs a and b with different domain names
        config_a = domain_config.model_copy()
        config_a.domain = "a"
        config_b = domain_config.model_copy()
        config_b.domain = "b"
        self.domain_config.storage.file_contents = {  # type: ignore
            "domain_config_a.yaml": yaml.safe_dump(config_a.to_dict()).encode(),
            "domain_config_b.yaml": yaml.safe_dump(config_b.to_dict()).encode(),
        }
        # when fetching domain configs from this path
        result = self.domain_config.fetch_configs(location=path)
        # then two domain configs are returned
        assert len(result) == 2
        assert set(result.keys()) == {"a", "b"}

    def test_exception_if_config_already_exists(self, domain_config: DomainConfigDTO):
        # given a path with two files for the same domain
        path = "good_path"
        matching_files = ["domain_config_a.yaml", "domain_config_a_copy.yaml"]
        self.domain_config.storage.found_objects = matching_files  # type: ignore
        config_a = domain_config.model_copy()
        config_a.domain = "a"
        self.domain_config.storage.file_contents = {  # type: ignore
            "domain_config_a.yaml": yaml.safe_dump(config_a.to_dict()).encode(),
            "domain_config_a_copy.yaml": yaml.safe_dump(config_a.to_dict()).encode(),
        }
        with pytest.raises(DomainConfigAlreadyExistsError):
            _ = self.domain_config.fetch_configs(location=path)

    def test_save_config_writes_correctly(self, domain_config: DomainConfigDTO):
        # given a fresh DummyStorage and DomainConfig
        storage = DummyStorage()
        manager = DomainConfig(storage=storage)  # type: ignore
        location = "some/location"
        config = domain_config.model_copy()
        config.domain = "testdomain"
        # when saving config
        manager.save_config(location, config)
        # then the correct file is written
        expected_filename = "domain_config_testdomain.yaml"
        expected_path = location + "/" + expected_filename
        assert expected_path in storage.written_files
        # and the content is valid YAML for the config
        written_bytes = storage.written_files[expected_path]
        loaded = yaml.safe_load(written_bytes)
        assert loaded["domain"] == "testdomain"

    def test_save_config_appends_slash_if_missing(self, domain_config: DomainConfigDTO):
        storage = DummyStorage()
        manager = DomainConfig(storage=storage)  # type: ignore
        location = "some/location"  # no trailing slash
        config = domain_config.model_copy()
        config.domain = "abc"
        manager.save_config(location, config)
        expected_path = "some/location/domain_config_abc.yaml"
        assert expected_path in storage.written_files

    def test_save_config_with_trailing_slash(self, domain_config: DomainConfigDTO):
        storage = DummyStorage()
        manager = DomainConfig(storage=storage)  # type: ignore
        location = "some/location/"  # with trailing slash
        config = domain_config.model_copy()
        config.domain = "xyz"
        manager.save_config(location, config)
        expected_path = "some/location/domain_config_xyz.yaml"
        assert expected_path in storage.written_files
