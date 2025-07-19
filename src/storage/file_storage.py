from typing import Dict, List

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
from src.dtos import LocationDTO, Store
from src.config import Config


class FileStorageError(
    StorageError,
):
    """"""


class ObjectIsNotAFileError(FileStorageError):
    """Raised when a directory is accessed as a file."""


class FileStorage(IStorage):
    """
    Handles files in Google Cloud Storage or local file system. Must conform to
    IStorage interfaces defined by all clients, e.g. domain_config, report, specification.
    """

    protocols: Dict[Store, AbstractFileSystem]
    default_encoding: str = "utf-8"

    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        self.protocols = {
            Store.LOCAL: LocalFileSystem(auto_mkdir=True),
            Store.MEMORY: MemoryFileSystem(),  # for testing purpose
        }
        if self.config.DATATESTER_USE_GCS_STORAGE:
            if GCSFileSystem is None:
                raise ImportError("GCSFileSystem is not installed")
            self.protocols[Store.GCS] = GCSFileSystem(
                project=self.config.DATATESTER_GCP_PROJECT
            )

    def _fs(self, path: LocationDTO) -> AbstractFileSystem:
        fs = self.protocols.get(path.store)
        if fs is None:
            raise StorageTypeUnknownError(f"Storage type {path.store} not supported")

        return fs

    def _protocol(self, fs: AbstractFileSystem) -> Store:
        if isinstance(fs, MemoryFileSystem):
            return Store.MEMORY
        elif isinstance(fs, LocalFileSystem):
            return Store.LOCAL
        elif GCSFileSystem is not None and isinstance(fs, GCSFileSystem):
            return Store.GCS
        else:
            raise StorageTypeUnknownError(f"Storage type {fs} not supported")

    def _exists(self, path: LocationDTO) -> bool:
        fs = self._fs(path=path)

        try:
            exists = fs.exists(path.path)
        except Exception as err:
            raise FileStorageError() from err

        return exists

    def list(self, path: LocationDTO) -> list[LocationDTO]:
        """
        Lists all files in given storage location. Only returns files at top level,
        not from subfolders.
        """
        if not self._exists(path=path):
            raise ObjectNotFoundError(str(path))
        fs = self._fs(path)
        files: list[LocationDTO] = []
        if fs.isfile(path.path):
            files.append(path)
        else:
            objects = fs.ls(path.path, detail=False)
            for object_ in objects:
                try:
                    if fs.isfile(object_):
                        protocol = self._protocol(fs).value.lower() + "://"
                        file_location = LocationDTO(protocol).append(object_)
                        files.append(file_location)
                except Exception:
                    continue
        return files

    def read(self, path: LocationDTO) -> bytes:
        """See interface definition."""

        fs = self._fs(path=path)

        if not self._exists(path):
            raise ObjectNotFoundError(str(path))

        if fs.isdir(path.path):
            raise ObjectIsNotAFileError(str(path))

        try:
            with fs.open(path.path, mode="rb", encoding=self.default_encoding) as file:
                content = file.read()
        except Exception as err:
            raise FileStorageError() from err

        return content

    def write(self, content: bytes, path: LocationDTO):
        """
        Writes bytecontent to specified path on local or gcs filesystem. Parent folders
        of specified path/file are auto-created if they don't exist.
        """

        fs = self._fs(path)

        try:
            with fs.open(path.path, mode="wb") as file:
                file.write(content)
        except Exception as err:
            raise FileStorageError() from err

    @property
    def supported_storage_types(self) -> List[Store]:
        """See interface definition."""

        return list(self.protocols.keys())
