from src.storage.i_storage_factory import IStorageFactory
from src.storage.i_storage import IStorage, StorageTypeUnknownError
from src.storage.i_formatter_factory import IFormatterFactory
from src.storage.file_storage import FileStorage
from src.storage.dict_storage import DictStorage
from src.dtos.location import LocationDTO, Store
from src.config import Config


class StorageFactory(IStorageFactory):
    """Factory for creating storage implementations based on location type."""

    def __init__(self, config: Config, formatter_factory: IFormatterFactory):
        self.config = config
        self.formatter_factory = formatter_factory
        self._dict_storage: DictStorage | None = None

    def get_storage(self, location: LocationDTO) -> IStorage:
        """
        Creates and returns an appropriate storage implementation based on the
        location type.

        Args:
            location: LocationDTO containing the storage type information

        Returns:
            IStorage: Storage implementation matching the location type

        Raises:
            StorageTypeUnknownError: If the location type is not supported
        """
        match location.store:
            case Store.LOCAL | Store.GCS | Store.MEMORY:
                return FileStorage(
                    self.config, location.store, self.formatter_factory
                )
            case Store.DICT:
                if self._dict_storage is None:
                    self._dict_storage = DictStorage(self.formatter_factory)
                return self._dict_storage
            case _:
                raise StorageTypeUnknownError(
                    f"Storage type {location.store} not supported"
                )
