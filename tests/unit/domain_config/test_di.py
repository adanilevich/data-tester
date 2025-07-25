import pytest
from src.domain_config.dependency_injection import DomainConfigDependencyInjector
from src.config import Config
from src.storage import DictStorage, FileStorage
import os

# Given-When-Then style tests for DomainConfigDependencyInjector


# Helper to make a config with a specific location and env
def make_config(location: str, env: str = "LOCAL"):
    os.environ["DATATESTER_ENV"] = env
    config = Config()
    config.DATATESTER_DOMAIN_CONFIGS_LOCATION = location
    return config


def test_injector_uses_dict_storage_for_dict_location():
    # Given: a config with DICT location
    config = make_config("dict://my/path")
    # When: creating the injector
    injector = DomainConfigDependencyInjector(config)
    # Then: storage is DictStorage
    assert isinstance(injector.storage, DictStorage)


def test_injector_uses_file_storage_for_local_location():
    # Given: a config with LOCAL location
    config = make_config("local://my/path")
    # When: creating the injector
    injector = DomainConfigDependencyInjector(config)
    # Then: storage is FileStorage
    assert isinstance(injector.storage, FileStorage)


def test_injector_uses_file_storage_for_gcs_location():
    # Given: a config with GCS location
    config = make_config("gcs://my/path")
    # When: creating the injector
    injector = DomainConfigDependencyInjector(config)
    # Then: storage is FileStorage
    assert isinstance(injector.storage, FileStorage)


def test_injector_uses_file_storage_for_memory_location():
    # Given: a config with MEMORY location
    config = make_config("memory://my/path")
    # When: creating the injector
    injector = DomainConfigDependencyInjector(config)
    # Then: storage is FileStorage
    assert isinstance(injector.storage, FileStorage)


def test_injector_raises_if_location_not_set():
    # Given: a config with no DATATESTER_DOMAIN_CONFIGS_LOCATION
    config = Config()
    config.DATATESTER_DOMAIN_CONFIGS_LOCATION = None # type: ignore
    # When/Then: creating the injector raises ValueError
    with pytest.raises(ValueError) as excinfo:
        DomainConfigDependencyInjector(config)
    assert "DATATESTER_DOMAIN_CONFIGS_LOCATION is not set" in str(excinfo.value)
