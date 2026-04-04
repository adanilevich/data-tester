from __future__ import annotations
from enum import Enum

from pydantic import field_validator

from src.dtos.dto import DTO


#TODO: change enum strings to upper case
class StorageType(Enum):
    LOCAL = "local"
    DICT = "dict"
    MEMORY = "memory"
    GCS = "gcs"
    UNSUPPORTED = "unsupported"


class ObjectType(Enum):
    TESTRUN = "testrun"
    TESTCASE_REPORT = "testcase_report"
    TESTRUN_REPORT = "testrun_report"
    TESTSET = "testset"
    DOMAIN_CONFIG = "domain_config"
    SPECIFICATION = "specification"
    UNKNOWN = "unknown"


class LocationDTO(DTO):
    path: str

    def __init__(self, path: str):
        super().__init__(path=path)  # type: ignore

    @field_validator("path")
    @classmethod
    def validate_path(cls, v):
        if len(v.split("://")) != 2:
            raise ValueError(f"Invalid path: one storage qualifier '://' expected: {v}")
        # check dots only in the last path segment (filename), not in directories
        path_part = v.split("://")[1]
        stripped = path_part.rstrip("/")
        filename = stripped.rsplit("/", 1)[-1] if "/" in stripped else stripped
        if len(filename.split(".")) > 2:
            if v.startswith("duckdb://"):  # database paths are separated by '.'
                pass
            else:
                raise ValueError(f"Invalid path: only one '.' allowed in filename: {v}")
        return v

    def model_post_init(self, __context):
        self._format_path()

    @property
    def storage_type(self) -> StorageType:
        return StorageType(self.path.split("://")[0])

    @property
    def is_file(self) -> bool:
        if self.is_db:
            return False
        elif "." in self.path:  # assume than non-db paths with "." are files
            return True
        else:  # assume that non-db paths without "." are folders
            return False

    @property
    def is_dir(self) -> bool:
        if not self.is_file and not self.is_db:
            return True
        else:
            return False

    @property
    def is_db(self) -> bool:
        return True if self.path.startswith("duckdb://") else False

    @property
    def filename(self) -> str | None:
        if not self.is_file:
            return None
        else:
            return self.path.split("/")[-1]

    def append(self, subpath: str) -> LocationDTO:
        if self.is_file or self.is_db:
            raise ValueError("File and DB locations cannot be extended")

        while subpath.startswith("/"):
            subpath = subpath[1:]

        return LocationDTO(self.path + subpath)

    def _format_path(self):
        if self.is_db:
            pass
        elif self.is_file:
            pass
        elif self.is_dir:
            if not self.path.endswith("/"):
                self.path += "/"
        else:
            raise ValueError(f"Unkown location path type: {self.path}")


class ObjectLocationDTO(DTO):
    location: LocationDTO
    located_object_id: str
    object_type: ObjectType
