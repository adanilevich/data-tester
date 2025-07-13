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

    protocols: Dict[str, AbstractFileSystem]
    default_encoding: str = "utf-8"

    def __init__(self, config: Config | None = None):
        self.config: Config = config or Config()
        self.protocols = {
            "local://": LocalFileSystem(auto_mkdir=True),
            "memory://": MemoryFileSystem(),  # for testing purpose
        }
        if self.config.DATATESTER_USE_GCS_STORAGE:
            self.protocols["gs://"] = GCSFileSystem(
                project=self.config.DATATESTER_GCP_PROJECT)

    def _fs(self, path: str) -> AbstractFileSystem:
        for protocol, fs in self.protocols.items():
            if path.startswith(protocol):
                return fs

        raise StorageTypeUnknownError(str(path))

    def _protocol(self, fs: AbstractFileSystem) -> str:
        if isinstance(fs, MemoryFileSystem):
            return "memory"
        elif isinstance(fs, LocalFileSystem):
            return "local"
        elif isinstance(fs, GCSFileSystem):
            return "gs"
        else:
            raise StorageTypeUnknownError(str(fs))

    def _exists(self, path: str) -> bool:
        fs = self._fs(path=path)

        try:
            exists = fs.exists(path)
        except Exception as err:
            msg = err.__class__.__name__ + ": " + str(err)
            raise FileStorageError(msg) from err

        return exists

    def find(self, path: str) -> List[str]:
        """Returns all files in path, prefixed with the protocol"""

        if not self._exists(path):
            raise ObjectNotFoundError(str(path))

        fs = self._fs(path)
        files = []
        if fs.isfile(path):
            files.append(path)
        else:
            objects = fs.ls(path, detail=False)
            for object in objects:
                try:
                    if fs.isfile(object):
                        files.append(object)
                except Exception:
                    continue

        return [self._protocol(fs) + "://" + file.lstrip("/\\") for file in files]

    def read(self, path: str) -> bytes:
        """See interface definition."""

        fs = self._fs(path=path)

        if not self._exists(path):
            raise ObjectNotFoundError(str(path))

        if fs.isdir(path):
            raise ObjectIsNotAFileError(str(path))

        try:
            with fs.open(path, mode="rb", encoding=self.default_encoding) as file:
                content = file.read()
        except Exception as err:
            msg = err.__class__.__name__ + ": " + str(err)
            raise FileStorageError(msg) from err

        return content

    def write(self, content: bytes, path: str):
        """
        Writes bytecontent to specified path on local or gcs filesystem. Parent folders
        of specified path/file are auto-created if they don't exist.
        """

        fs = self._fs(path=path)

        try:
            with fs.open(path, mode="wb") as file:
                file.write(content)
        except Exception as err:
            msg = err.__class__.__name__ + ": " + str(err)
            raise FileStorageError(msg) from err

    @property
    def supported_storage_types(self) -> List[str]:
        """See interface definition."""


        return [protocol.split(":")[0] for protocol in self.protocols]
