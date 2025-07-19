from src.testset.dependency_injection import TestSetDependencyInjector
from src.config import Config
from src.storage.dict_storage import DictStorage
from src.storage.file_storage import FileStorage


def make_config(engine="DICT", location="dict://testsets/"):
    cfg = Config()
    cfg.DATATESTER_INTERNAL_STORAGE_ENGINE = engine
    cfg.DATATESTER_INTERNAL_TESTSET_LOCATION = location
    return cfg

def test_injector_dict_storage():
    # Given a config for DICT storage
    config = make_config(engine="DICT", location="dict://testsets/")
    # When creating the injector
    injector = TestSetDependencyInjector(config)
    # Then the storage is a DictStorage and location is set
    assert isinstance(injector.storage, DictStorage)
    assert injector.storage_location.path == "dict://testsets/"

def test_injector_file_storage():
    # Given a config for LOCAL storage
    config = make_config(engine="LOCAL", location="local://testsets/")
    # When creating the injector
    injector = TestSetDependencyInjector(config)
    # Then the storage is a FileStorage and location is set
    assert isinstance(injector.storage, FileStorage)
    assert injector.storage_location.path == "local://testsets/"
