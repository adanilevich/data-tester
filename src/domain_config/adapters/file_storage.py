from typing import Dict, List

from fsspec import AbstractFileSystem  # type: ignore
from fsspec.implementations.local import LocalFileSystem  # type: ignore
from fsspec.implementations.memory import MemoryFileSystem  # type: ignore
from gcsfs import GCSFileSystem  # type: ignore

from src.domain_config.ports import IStorage, StorageError
from src.config import Config


class FileStorageError(StorageError):
    """"""


class ObjectNotFoundError(FileStorageError):
    """"""


class ObjectIsNotAFileError(FileStorageError):
    """"""


class StorageTypeUnknownError(FileStorageError):
    """"""


class FileStorage(IStorage):
    """Handles files in Google Cloud Storage or local file system"""

    protocols: Dict[str, AbstractFileSystem]

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

    def protocol(self, path: str) -> str:

        if not self.protocol_is_valid(path):
            raise StorageTypeUnknownError(f"Unknown storage type: {path}")

        return path.split(":")[0]

    def protocol_is_valid(self, path: str) -> bool:
        return path.startswith(tuple(self.protocols.keys()))

    def exists(self, path: str) -> bool:

        if not self.protocol_is_valid(path):
            raise StorageTypeUnknownError(f"Path type unknown: {path}")

        try:
            exists = self._fs(path).exists(path)
        except Exception as err:
            msg = err.__class__.__name__ + ": " + str(err)
            raise FileStorageError(msg)

        return exists

    def find(self, path: str) -> List[str]:
        """Returns all files in path, prefixed with the protocol"""

        if not self.exists(path):
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

        return [self.protocol(path) + "://" + file.lstrip("/\\") for file in files]

    def read_text(self, path: str, encoding: str | None = None,
                  errors: str | None = None, newline: str | None = None) -> str:

        fs = self._fs(path=path)

        if not self.exists(path):
            raise ObjectNotFoundError(f"Object not found: {path}")

        if fs.isdir(path):
            raise ObjectIsNotAFileError(f"Object is a directory: {path}")

        try:
            with fs.open(
                path, mode="r", encoding=encoding, errors=errors, newline=newline
            ) as file:
                content = file.read()
        except Exception as err:
            msg = err.__class__.__name__ + ": " + str(err)
            raise StorageError(msg)

        return content

    def read_bytes(self, path: str) -> bytes:

        fs = self._fs(path=path)

        if not self.exists(path):
            raise ObjectNotFoundError(f"Object not found: {path}")

        if fs.isdir(path):
            raise ObjectIsNotAFileError(f"Object is a directory: {path}")

        try:
            with fs.open(path, mode="rb") as file:
                content = file.read()
        except Exception as err:
            msg = err.__class__.__name__ + ": " + str(err)
            raise StorageError(msg)

        return content
