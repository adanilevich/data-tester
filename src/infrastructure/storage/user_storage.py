from typing import List

from fsspec import AbstractFileSystem
from fsspec.implementations.local import LocalFileSystem
from fsspec.implementations.memory import MemoryFileSystem

try:
    from gcsfs import GCSFileSystem  # ty: ignore[unresolved-import]
except ImportError:
    GCSFileSystem = None

from src.dtos.storage_dtos import LocationDTO, StorageType
from src.infrastructure_ports import (
    IUserStorage,
    ObjectNotFoundError,
    StorageError,
    StorageTypeUnknownError,
)


class UserStorageFileError(StorageError):
    """Error raised by file-based user storage implementations."""


class UserStorageFile(IUserStorage):
    """Base class for fsspec-based user storage. Read-only for user-managed files."""

    def __init__(self, fs: AbstractFileSystem, storage_type: StorageType):
        self.fs: AbstractFileSystem = fs
        self.storage_type: StorageType = storage_type

    def _validate_storage_type(self, location: LocationDTO) -> None:
        if location.storage_type != self.storage_type:
            raise StorageTypeUnknownError(
                f"Path storage type {location.storage_type} does not match "
                f"storage type {self.storage_type}"
            )

    def read_object(self, location: LocationDTO) -> bytes:
        self._validate_storage_type(location)

        try:
            if not self.fs.exists(location.path):
                raise ObjectNotFoundError(str(location))
        except ObjectNotFoundError:
            raise
        except Exception as err:
            raise UserStorageFileError(f"Error checking existence: {location}") from err

        try:
            with self.fs.open(location.path, mode="rb") as f:
                return f.read()
        except Exception as err:
            raise UserStorageFileError(f"Error reading from: {location}") from err

    def list_objects(self, location: LocationDTO) -> List[LocationDTO]:
        self._validate_storage_type(location)

        try:
            if not self.fs.exists(location.path):
                raise ObjectNotFoundError(str(location))
        except ObjectNotFoundError:
            raise
        except Exception as err:
            raise UserStorageFileError(f"Error checking existence: {location}") from err

        if self.fs.isfile(location.path):
            return [location]

        file_locations: List[LocationDTO] = []
        try:
            objects = self.fs.ls(location.path, detail=False)
        except Exception as err:
            raise UserStorageFileError(f"Error listing: {location}") from err

        protocol = self.storage_type.value.lower() + "://"
        for obj_path in objects:
            try:
                if self.fs.isfile(obj_path):
                    file_locations.append(LocationDTO(protocol + obj_path))
            except Exception:
                continue

        return file_locations


class MemoryUserStorage(UserStorageFile):
    def __init__(self) -> None:
        super().__init__(MemoryFileSystem(), StorageType.MEMORY)


class LocalUserStorage(UserStorageFile):
    def __init__(self) -> None:
        super().__init__(LocalFileSystem(auto_mkdir=True), StorageType.LOCAL)


class GcsUserStorage(UserStorageFile):
    def __init__(self, gcp_project: str) -> None:
        if GCSFileSystem is None:
            raise ImportError("gcsfs is not installed. Install with: uv sync --extra gcs")
        super().__init__(GCSFileSystem(project=gcp_project), StorageType.GCS)
