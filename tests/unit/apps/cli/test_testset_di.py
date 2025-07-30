from src.apps.cli.testset_di import TestSetDependencyInjector
from src.config import Config
from src.drivers.cli import CliTestSetManager
from src.domain.testset import TestSetCommandHandler


def make_config(engine="DICT", location="dict://testsets/"):
    cfg = Config()
    cfg.DATATESTER_INTERNAL_STORAGE_ENGINE = engine
    cfg.DATATESTER_INTERNAL_TESTSET_LOCATION = location
    return cfg


def test_cli_testset_manager():
    config = make_config()
    injector = TestSetDependencyInjector(config)
    cli_testset_manager = injector.cli_testset_manager()
    assert isinstance(cli_testset_manager, CliTestSetManager)
    assert cli_testset_manager.storage_location.path == "dict://testsets/"
    assert isinstance(cli_testset_manager.testset_handler, TestSetCommandHandler)
    assert cli_testset_manager.testset_handler.storage_factory == injector.storage_factory
