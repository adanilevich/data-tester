import pytest
from src.testset.dependency_injection import CliTestSetDependencyInjector
from src.config import Config
from src.storage.dict_storage import DictStorage
from src.storage.file_storage import FileStorage


def make_config(engine="DICT", location="dict://testsets/"):
    cfg = Config()
    cfg.INTERNAL_STORAGE_ENGINE = engine
    cfg.INTERNAL_TESTSET_LOCATION = location
    return cfg

def test_injector_dict_storage():
    # Given a config for DICT storage
    config = make_config(engine="DICT", location="dict://testsets/")
    # When creating the injector
    injector = CliTestSetDependencyInjector(config)
    # Then the storage is a DictStorage and location is set
    assert isinstance(injector.storage, DictStorage)
    assert injector.storage_location.path == "dict://testsets/"

def test_injector_file_storage():
    # Given a config for LOCAL storage
    config = make_config(engine="LOCAL", location="local://testsets/")
    # When creating the injector
    injector = CliTestSetDependencyInjector(config)
    # Then the storage is a FileStorage and location is set
    assert isinstance(injector.storage, FileStorage)
    assert injector.storage_location.path == "local://testsets/"

def test_injector_missing_engine():
    # Given a config with missing INTERNAL_STORAGE_ENGINE
    config = Config()
    config.INTERNAL_STORAGE_ENGINE = None  # type: ignore
    config.INTERNAL_TESTSET_LOCATION = "dict://testsets/"
    # When creating the injector, Then it raises ValueError
    with pytest.raises(ValueError) as excinfo:
        CliTestSetDependencyInjector(config)
    assert "INTERNAL_STORAGE_ENGINE is not set" in str(excinfo.value)

def test_injector_missing_location():
    # Given a config with missing INTERNAL_TESTSET_LOCATION
    config = Config()
    config.INTERNAL_STORAGE_ENGINE = "DICT"
    config.INTERNAL_TESTSET_LOCATION = None
    # When creating the injector, Then it raises ValueError
    with pytest.raises(ValueError) as excinfo:
        CliTestSetDependencyInjector(config)
    assert "INTERNAL_TESTSET_LOCATION is not set" in str(excinfo.value)

def test_injector_unsupported_engine():
    # Given a config with unsupported engine
    config = make_config(engine="UNSUPPORTED", location="dict://testsets/")
    # When creating the injector, Then it raises ValueError
    with pytest.raises(ValueError) as excinfo:
        CliTestSetDependencyInjector(config)
    assert "INTERNAL_STORAGE_ENGINE UNSUPPORTED is not supported" in str(excinfo.value)
