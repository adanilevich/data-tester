from typing import List

from fsspec import AbstractFileSystem  # type: ignore
from fsspec.implementations.local import LocalFileSystem  # type: ignore
from fsspec.implementations.memory import MemoryFileSystem  # type: ignore

try:
    from gcsfs import GCSFileSystem  # type: ignore
except ImportError:
    GCSFileSystem = None

from src.storage.i_storage import (
    IStorage,
    StorageError,
    ObjectNotFoundError,
    StorageTypeUnknownError,
)
from src.storage.i_formatter_factory import IFormatterFactory
from src.dtos import LocationDTO, Store, DTO, StorageObject, ObjectLocationDTO
from src.config import Config


class FileStorageError(
    StorageError,
):
    """"""


class ObjectIsNotAFileError(FileStorageError):
    """Raised when a directory is accessed as a file."""


class FileStorage(IStorage):
    """
    Handles files in Google Cloud Storage or local file system. Can handle objects in
    application-internal storage, in this case DTO objects are read and written.
    Can also be used for user-managed storage - then raw bytes are read and written.
    """

    default_encoding: str = "utf-8"

    def __init__(
        self, config: Config, storage_type: Store, formatter_factory: IFormatterFactory
    ):
        self.config = config
        self.storage_type = storage_type
        self.formatter_factory = formatter_factory
        self.fs = self._create_filesystem(storage_type)

    def _create_filesystem(self, storage_type: Store) -> AbstractFileSystem:
        """Create the appropriate filesystem based on storage type."""
        match storage_type:
            case Store.LOCAL:
                return LocalFileSystem(auto_mkdir=True)
            case Store.MEMORY:
                return MemoryFileSystem()
            case Store.GCS:
                if not self.config.DATATESTER_USE_GCS_STORAGE:
                    raise StorageTypeUnknownError("GCS storage is not enabled in config")
                if GCSFileSystem is None:
                    raise ImportError("GCSFileSystem is not installed")
                return GCSFileSystem(project=self.config.DATATESTER_GCP_PROJECT)
            case _:
                raise StorageTypeUnknownError(
                    f"Storage type {storage_type} not supported"
                )

    def _exists(self, path: LocationDTO) -> bool:
        self._validate_storage_type(path)
        try:
            exists = self.fs.exists(path.path)
        except Exception as err:
            raise FileStorageError() from err

        return exists

    def _validate_storage_type(self, path: LocationDTO) -> None:
        """Validate that the path's storage type matches this instance."""
        if path.store != self.storage_type:
            raise StorageTypeUnknownError(
                f"Path storage type {path.store} does not match "
                f"FileStorage type {self.storage_type}"
            )

    def write(self, dto: DTO, object_type: StorageObject, location: LocationDTO):
        """
        Stores a DTO object to storage, serialized according to internal format.
        """
        self._validate_storage_type(location)

        formatter = self.formatter_factory.get_formatter(object_type)
        serialized_data = formatter.serialize(dto)

        object_key = formatter.get_object_key(dto.object_id, object_type)
        file_location = location.append(object_key)

        try:
            with self.fs.open(file_location.path, mode="wb") as file:
                file.write(serialized_data)
        except Exception as err:
            raise FileStorageError() from err

    def read(
        self, object_type: StorageObject, object_id: str, location: LocationDTO
    ) -> DTO:
        """
        Retrieves and deserializes a DTO object from (internal) storage.
        """
        self._validate_storage_type(location)

        formatter = self.formatter_factory.get_formatter(object_type)
        object_key = formatter.get_object_key(object_id, object_type)

        file_location = location.append(object_key)

        if not self._exists(file_location):
            raise ObjectNotFoundError(f"Object {object_id} of type {object_type}")

        if self.fs.isdir(file_location.path):
            raise ObjectIsNotAFileError(str(file_location))

        try:
            with self.fs.open(
                file_location.path, mode="rb", encoding=self.default_encoding
            ) as file:
                content = file.read()
        except Exception as err:
            raise FileStorageError() from err

        return formatter.deserialize(content, object_type)

    def write_bytes(self, content: bytes, location: LocationDTO):
        """
        Stores raw bytes content to the specified location. Should only be used for
        storing user-facing artifacts in user-managed storage where serialization and
        naming conventions are handled by the clients of the specific implementation of
        IStorage.
        """
        self._validate_storage_type(location)

        try:
            with self.fs.open(location.path, mode="wb") as file:
                file.write(content)
        except Exception as err:
            raise FileStorageError() from err

    def read_bytes(self, location: LocationDTO) -> bytes:
        """
        Reads raw bytes content from the specified location. Should only be used for
        reading user-facing artifacts from user-managed storage where serialization and
        naming conventions are handled by the clients of the specific implementation of
        IStorage.
        """
        self._validate_storage_type(location)

        if not self._exists(location):
            raise ObjectNotFoundError(str(location))

        if self.fs.isdir(location.path):
            raise ObjectIsNotAFileError(str(location))

        try:
            with self.fs.open(
                location.path, mode="rb", encoding=self.default_encoding
            ) as file:
                content = file.read()
        except Exception as err:
            raise FileStorageError() from err

        return content

    def list(
        self, location: LocationDTO, object_type: StorageObject
    ) -> List[ObjectLocationDTO]:
        """
        Lists all objects of the specified type in the given location. This is meant for
        listing objects from application-internal storage.
        """
        self._validate_storage_type(location)

        if not self._exists(location):
            raise ObjectNotFoundError(str(location))

        formatter = self.formatter_factory.get_formatter(object_type)
        object_locations = []

        if self.fs.isfile(location.path):
            # Single file case
            filename = location.filename
            if filename and formatter.check_filename(filename, object_type):
                try:
                    object_id = formatter.get_object_id(filename, object_type)
                    object_locations.append(ObjectLocationDTO(
                        location=location,
                        located_object_id=object_id,
                        object_type=object_type
                    ))
                except ValueError:
                    # Skip files that don't match the naming convention
                    pass
        else:
            objects = self.fs.ls(location.path, detail=False)
            for object_path in objects:
                try:
                    if self.fs.isfile(object_path):
                        filename = object_path.split("/")[-1]
                        if formatter.check_filename(filename, object_type):
                            try:
                                object_id = formatter.get_object_id(filename, object_type)
                                protocol = self.storage_type.value.lower() + "://"
                                file_location = LocationDTO(protocol + object_path)
                                object_locations.append(ObjectLocationDTO(
                                    location=file_location,
                                    located_object_id=object_id,
                                    object_type=object_type
                                ))
                            except ValueError:
                                # Skip files that don't match the naming convention
                                continue
                except Exception:
                    continue

        return object_locations

    def list_files(self, location: LocationDTO) -> List[LocationDTO]:
        """
        Lists all files in the given location regardless of type. This is meant for
        listing user-managed files like specifications. Client must be able to handle
        the naming conventaions and deserialization of the files.
        """
        self._validate_storage_type(location)

        if not self._exists(location):
            raise ObjectNotFoundError(str(location))

        file_locations = []

        if self.fs.isfile(location.path):
            # Single file case
            file_locations.append(location)
        else:
            objects = self.fs.ls(location.path, detail=False)
            for object_path in objects:
                try:
                    if self.fs.isfile(object_path):
                        protocol = self.storage_type.value.lower() + "://"
                        file_location = LocationDTO(protocol + object_path)
                        file_locations.append(file_location)
                except Exception:
                    continue

        return file_locations

    @property
    def supported_storage_types(self) -> List[Store]:
        """See interface definition."""
        return [self.storage_type]
