from typing import List, Optional
from fsspec import AbstractFileSystem  # type: ignore
from fsspec.implementations.local import LocalFileSystem  # type: ignore
from gcsfs import GCSFileSystem  # type: ignore

from src.domain_config.ports import IStorage


class FileStorage(IStorage):
    """Handles files in Google Cloud Storage or local file system"""

    def __init__(self):
        self.gcs = GCSFileSystem()
        self.fs = LocalFileSystem()

    def is_valid_location(self, location: str) -> bool:
        valid_prefixes = ("/", "gs://")
        if location.startswith(valid_prefixes):
            fs = self._fs(location)
            return True if fs.exists(location) else False
        else:
            return False

    def _fs(self, location: str) -> AbstractFileSystem:
        if location.startswith("gs://"):
            return self.gcs
        elif location.startswith("/"):
            return self.fs
        else:
            raise ValueError(f"Unknown location type: {location}")

    def list_objects(self, location: str) -> List[str]:
        fs = self._fs(location=location)

        if not fs.exists(location):
            return []

        if fs.isfile(location):
            return [location]
        elif fs.isdir(location):
            files = [file for file in fs.ls(location) if fs.isfile(file)]
            return files
        else:  # this should never happen
            raise ValueError(f"Location is neither dir nor file: {location}")

    def load_object(self, location: str) -> Optional[bytes | str]:

        fs = self._fs(location=location)

        if not fs.exists(location):
            return None

        if fs.isdir(location):
            return None
        else:
            with fs.open(location, "r") as file:
                content = file.read()
            return content
