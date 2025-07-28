from __future__ import annotations
from enum import Enum

from pydantic import field_validator

from src.dtos.dto import DTO


class Store(Enum):
    LOCAL = "local"
    GCS = "gcs"
    S3 = "s3"
    DICT = "dict"
    MEMORY = "memory"
    BQ = "bq"
    UNKNOWN = "unknown"
    UPLOAD = "upload"
    DUCKDB = "duckdb"
    DUMMY = "dummy"


class StorageObject(Enum):
    """
    Object types which can be stored in internal storage. Correspond to the defined
    DTO objects.
    """

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
            raise ValueError("Invalid path")
        return v

    def model_post_init(self, __context):
        self.path = self._format(self.path)

    @property
    def store(self):
        return Store(self.path.split("://")[0])

    @property
    def filename(self):
        if "." not in self.path:
            return None
        else:
            return self.path.split("/")[-1]

    def append(self, subpath: str) -> LocationDTO:
        if "." in self.path:
            raise ValueError("File location cannot be extended")
        while subpath.startswith("/"):
            subpath = subpath[1:]
        else:
            path_ = self._format(self.path)
            path_ = self._format(path_ + subpath)
        return LocationDTO(path_)

    def _format(self, path: str):
        # in case of a file, we don't need to add a trailing slash
        if "." in path:
            pass
        # in case of a directory, we need to add a trailing slash
        else:
            if not path.endswith("/"):
                path += "/"
        return path


class ObjectLocationDTO(DTO):
    location: LocationDTO
    located_object_id: str
    object_type: StorageObject
