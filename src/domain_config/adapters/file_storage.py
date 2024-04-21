from typing import Dict, List
import os

from fsspec import AbstractFileSystem  # type: ignore
from fsspec.implementations.local import LocalFileSystem  # type: ignore
from gcsfs import GCSFileSystem  # type: ignore

from src.domain_config.ports import IStorage, StorageError


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

        self._gcp_project = os.environ.get("DATA_TESTER_GCP_PROJECT")

        self.protocols = {
            "local:": LocalFileSystem(),
            "gs://": GCSFileSystem(project=self._gcp_project)
        }

    def _fs(self, path: str) -> AbstractFileSystem:

        for protocol, fs in self.protocols.items():
            if path.startswith(protocol):
                return fs

        raise StorageTypeUnknownError(f"Unknown location type: {path}")

    def _prefix_is_valid(self, path: str) -> bool:
        return path.startswith(tuple(self.protocols.keys()))

    def exists(self, path: str) -> bool:

        if not self._prefix_is_valid(path):
            raise StorageTypeUnknownError(f"Path type unknown: {path}")

        try:
            exists = self._fs(path).exists(path)
        except Exception as err:
            msg = err.__class__.__name__ + ": " + str(err)
            raise FileStorageError(msg)

        return exists

    def _prefix(self, fs: AbstractFileSystem) -> str:

        for protocol, filesystem in self.protocols.items():
            if isinstance(fs, filesystem.__class__):
                return protocol
        raise StorageTypeUnknownError(f"Unknown storage type: {str(fs)}")

    def find(self, path: str) -> List[str]:

        fs = self._fs(path)

        if not self.exists(path):
            raise ObjectNotFoundError(f"Location doesn't exist: {path}")

        if fs.isfile(path):
            files = [path]
        else:
            files = []
            objects = fs.ls(path)
            for object in objects:
                try:
                    if fs.isfile(object):
                        files.append(object)
                except Exception:
                    continue

        return files

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
