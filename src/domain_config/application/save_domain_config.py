from src.domain_config.ports import (
    ISaveDomainConfigCommandHandler, SaveDomainConfigCommand, IStorage)
from src.domain_config.core import DomainConfig


class SaveDomainConfigCommandHandler(ISaveDomainConfigCommandHandler):
    def __init__(self, storage: IStorage):
        self.storage = storage

    def save(self, command: SaveDomainConfigCommand) -> None:
        manager = DomainConfig(storage=self.storage)
        manager.save_config(location=command.location, config=command.config)
