from src.infrastructure_ports import IStorageFactory, IStorage, StorageTypeUnknownError
from .i_formatter_factory import IFormatterFactory
from .file_storage import FileStorage
from .dict_storage import DictStorage
from src.dtos.location import LocationDTO, Store


class StorageFactory(IStorageFactory):
    """Factory for creating storage implementations based on location type."""

    def __init__(self, formatter_factory: IFormatterFactory):
        self.formatter_factory: IFormatterFactory = formatter_factory
        self._dict_storage: DictStorage | None = None
        self._mem_storage: FileStorage | None = None

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
            case Store.LOCAL | Store.GCS:
                return FileStorage(location.store, self.formatter_factory)
            case Store.MEMORY:
                if self._mem_storage is None:
                    self._mem_storage = FileStorage(
                        location.store, self.formatter_factory)
                return self._mem_storage
            case Store.DICT:
                # dict storage is stateful, only assign if not already assigned
                if self._dict_storage is None:
                    self._dict_storage = DictStorage(self.formatter_factory)
                return self._dict_storage
            case _:
                raise StorageTypeUnknownError(
                    f"Storage type {location.store} not supported"
                )
