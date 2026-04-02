from src.infrastructure_ports import IStorageFactory, IStorage, StorageTypeUnknownError
from .i_formatter_factory import IFormatterFactory
from .file_storage import FileStorage
from .dict_storage import DictStorage
from src.dtos.storage import LocationDTO, StorageType


# TODO: make this a singleton to hold one Storage object of each type only
# HOWTO: https://stackoverflow.com/questions/6760685/what-is-the-best-way-of-implementing-a-singleton-in-python
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
        match location.storage_type:
            case StorageType.LOCAL | StorageType.GCS:
                return FileStorage(location.storage_type, self.formatter_factory)
            case StorageType.MEMORY:
                # memory storage is stateful, only assign if not already assigned
                if self._mem_storage is None:
                    self._mem_storage = FileStorage(
                        location.storage_type, self.formatter_factory)
                return self._mem_storage
            case StorageType.DICT:
                # dict storage is stateful, only assign if not already assigned
                if self._dict_storage is None:
                    self._dict_storage = DictStorage(self.formatter_factory)
                return self._dict_storage
            case _:
                raise StorageTypeUnknownError(
                    f"Storage type {location.storage_type} not supported"
                )
