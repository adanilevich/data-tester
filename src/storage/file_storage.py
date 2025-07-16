from typing import Dict, List

from fsspec import AbstractFileSystem  # type: ignore
from fsspec.implementations.local import LocalFileSystem  # type: ignore
from fsspec.implementations.memory import MemoryFileSystem  # type: ignore
from gcsfs import GCSFileSystem  # type: ignore

from src.domain_config.ports import (
    IStorage as IDomainConfigStorage,
    StorageError as DomainConfigStorageError,
)
from src.report.ports import (
    IStorage as IReportStorage,
    StorageError as ReportStorageError,
    ObjectNotFoundError as ReportStorageObjectNotFoundError,
    StorageTypeUnknownError as ReportStorageTypeUnknownError,
)
from src.dtos.location import LocationDTO, Store
from src.config import Config


class FileStorageError(DomainConfigStorageError, ReportStorageError):
    """"""


class ObjectNotFoundError(ReportStorageObjectNotFoundError):
    """"""


class ObjectIsNotAFileError(FileStorageError):
    """"""


class StorageTypeUnknownError(ReportStorageTypeUnknownError):
    """"""


class FileStorage(IDomainConfigStorage, IReportStorage):
    """
    Handles files in Google Cloud Storage or local file system. Must conform to
    IStorage interfaces defined by all clients, e.g. domain_config, report, specification.
    """

    protocols: Dict[Store, AbstractFileSystem]
    default_encoding: str = "utf-8"

    def __init__(self, config: Config | None = None):
        self.config: Config = config or Config()
        self.protocols = {
            Store.LOCAL: LocalFileSystem(auto_mkdir=True),
            Store.MEMORY: MemoryFileSystem(),  # for testing purpose
        }
        if self.config.DATATESTER_USE_GCS_STORAGE:
            self.protocols[Store.GCS] = GCSFileSystem(
                project=self.config.DATATESTER_GCP_PROJECT)

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
        elif isinstance(fs, GCSFileSystem):
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

    def find(self, path: LocationDTO) -> List[LocationDTO]:
        """Returns all files in path, prefixed with the protocol"""

        if not self._exists(path=path):
            raise ObjectNotFoundError(str(path))

        fs = self._fs(path)
        files: List[LocationDTO] = []
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
