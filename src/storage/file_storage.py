from typing import Any, Dict, List

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
    StorageError as ReportStorageError
)
from src.config import Config


class FileStorageError(DomainConfigStorageError, ReportStorageError):
    """"""


class ObjectNotFoundError(FileStorageError):
    """"""


class ObjectIsNotAFileError(FileStorageError):
    """"""


class StorageTypeUnknownError(FileStorageError):
    """"""


class ContentTypeUnknownError(FileStorageError):
    """"""


class FileStorage(IDomainConfigStorage, IReportStorage):
    """
    Handles files in Google Cloud Storage or local file system. Must conform to
    IStorage interfaces defined by all clients, e.g. domain_config, report, specification.
    """

    protocols: Dict[str, AbstractFileSystem]
    # list of known content types which are interpreted and read as text
    text_content_types: List[str] = ["application/yaml", "plain/text"]
    # list of known content types which are interpreted and read as bytes
    bytes_content_types: List[str] = [
            'application/vnd.opnexmlformats-officedocument.spreadsheetml.tmeplate',
            "application/octet-stream",
        ]

    def __init__(self):

        self.protocols = {
            "local://": LocalFileSystem(),
            "gs://": GCSFileSystem(project=Config().DATATESTER_GCP_PROJECT),
            "memory://": MemoryFileSystem(),  # for testing purpose
        }

    def _fs(self, path: str) -> AbstractFileSystem:

        for protocol, fs in self.protocols.items():
            if path.startswith(protocol):
                return fs

        raise StorageTypeUnknownError(f"Unknown location type: {path}")

    def _protocol(self, path: str) -> str:

        if not self._protocol_is_valid(path):
            raise StorageTypeUnknownError(f"Unknown storage type: {path}")

        return path.split(":")[0]

    def _protocol_is_valid(self, path: str) -> bool:
        return path.startswith(tuple(self.protocols.keys()))

    def _exists(self, path: str) -> bool:

        if not self._protocol_is_valid(path):
            raise StorageTypeUnknownError(f"Path type unknown: {path}")

        try:
            exists = self._fs(path).exists(path)
        except Exception as err:
            msg = err.__class__.__name__ + ": " + str(err)
            raise FileStorageError(msg) from err

        return exists

    def find(self, path: str) -> List[str]:
        """Returns all files in path, prefixed with the protocol"""

        if not self._exists(path):
            raise ObjectNotFoundError(f"Location doesn't exist: {path}")

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

        return [self._protocol(path) + "://" + file.lstrip("/\\") for file in files]

    def read(self, path: str, content_type: str, encoding: str | None = None) -> Any:

        fs = self._fs(path=path)

        if not self._exists(path):
            raise ObjectNotFoundError(f"Object not found: {path}")

        if fs.isdir(path):
            raise ObjectIsNotAFileError(f"Object is a directory: {path}")

        if content_type in self.text_content_types:
            read_mode = "r"
        elif content_type in self.bytes_content_types:
            read_mode = "rb"
        else:
            raise ContentTypeUnknownError(content_type)

        try:
            with fs.open(path, mode=read_mode, encoding=encoding,) as file:
                content = file.read()
        except Exception as err:
            msg = err.__class__.__name__ + ": " + str(err)
            raise FileStorageError(msg) from err

        return content

    def write(self, content: Any, path: str, content_type: str,
              enconding: str | None = None):
        raise NotImplementedError("Writing data not yet implemented for FileStorage")
