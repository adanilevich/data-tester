from typing import List

from .i_storage import (
    IStorage,
    StorageError,
    ObjectNotFoundError,
    StorageTypeUnknownError,
)
from .i_formatter_factory import IFormatterFactory
from src.dtos import LocationDTO, Store, DTO, StorageObject, ObjectLocationDTO


class DictStorageError(
    StorageError,
):
    """"""


class DictStorage(IStorage):
    """
    In-memory storage implementation using a dictionary. This is meant both for
    application-internal storage and user-managed storage. This is a simple
    implementation for testing purpose only - in production, use a real storage
    implementation like FileStorage or GCSStorage or database storages.
    """

    def __init__(self, formatter_factory: IFormatterFactory):
        self._storage: dict[str, bytes] = {}
        self.formatter_factory = formatter_factory

    def _check_storage_type(self, path: LocationDTO) -> None:
        """Check if the storage type is supported"""
        if path.store != Store.DICT:
            raise StorageTypeUnknownError(f"Storage type not supported: {path}")

    def write(self, dto: DTO, object_type: StorageObject, location: LocationDTO):
        """
        Stores a DTO object in memory, serialized according to internal format.
        This should only be used for storing application-internal objects.
        """
        self._check_storage_type(location)

        formatter = self.formatter_factory.get_formatter(object_type)
        serialized_data = formatter.serialize(dto)

        object_key = formatter.get_object_key(dto.object_id, object_type)
        full_path = location.path + object_key

        self._storage[full_path] = serialized_data

    def read(
        self, object_type: StorageObject, object_id: str, location: LocationDTO
    ) -> DTO:
        """
        Retrieves and deserializes a DTO object from memory.
        This should only be used for reading application-internal objects.
        """
        self._check_storage_type(location)

        formatter = self.formatter_factory.get_formatter(object_type)
        object_key = formatter.get_object_key(object_id, object_type)
        full_path = location.path + object_key

        if full_path not in self._storage:
            raise ObjectNotFoundError(f"Object {object_id} of type {object_type}")

        content = self._storage[full_path]
        return formatter.deserialize(content, object_type)

    def write_bytes(self, content: bytes, location: LocationDTO):
        """
        Stores raw bytes content in memory. This should only be used for storing
        user-facing artifacts in user-managed storage where serialization and
        naming conventions are handled by the clients.
        """
        self._check_storage_type(location)
        self._storage[location.path] = content

    def read_bytes(self, location: LocationDTO) -> bytes:
        """Reads raw bytes content from memory. This should only be used for reading
        user-facing artifacts from user-managed storage where serialization and
        naming conventions are handled by the clients.
        """
        self._check_storage_type(location)
        if location.path not in self._storage:
            raise ObjectNotFoundError(f"Path not found: {location}")
        return self._storage[location.path]

    def list(
        self, location: LocationDTO, object_type: StorageObject
    ) -> List[ObjectLocationDTO]:
        """
        Lists all objects of the specified type in memory. This is meant for
        listing objects from application-internal storage.
        """
        self._check_storage_type(location)

        formatter = self.formatter_factory.get_formatter(object_type)
        object_locations = []

        for stored_path in self._storage:
            if stored_path.startswith(location.path):
                # Extract filename from path
                relative_path = stored_path[len(location.path) :]
                if "/" not in relative_path:  # Top level only
                    filename = relative_path
                    if formatter.check_filename(filename, object_type):
                        try:
                            object_id = formatter.get_object_id(filename, object_type)
                            file_location = LocationDTO(stored_path)
                            object_locations.append(
                                ObjectLocationDTO(
                                    location=file_location,
                                    located_object_id=object_id,
                                    object_type=object_type,
                                )
                            )
                        except ValueError:
                            # Skip files that don't match the naming convention
                            continue

        return object_locations

    def list_files(self, location: LocationDTO) -> List[LocationDTO]:
        """
        Lists all files in the given location regardless of type. This is meant for
        listing user-managed files like specifications. Client must be able to handle
        the naming conventaions and deserialization of the files.
        """
        self._check_storage_type(location)

        file_locations = []

        for stored_path in self._storage:
            if stored_path.startswith(location.path):
                # Extract relative path from stored path
                relative_path = stored_path[len(location.path) :]
                if "/" not in relative_path:  # Top level only
                    file_location = LocationDTO(stored_path)
                    file_locations.append(file_location)

        return file_locations

    @property
    def supported_storage_types(self) -> List[Store]:
        """Returns supported storage types"""
        return [Store.DICT]
