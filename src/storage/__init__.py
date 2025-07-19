# flake8: noqa
from .file_storage import FileStorage
from .dict_storage import DictStorage
from .i_storage import (
    IStorage,
    StorageTypeUnknownError,
    StorageError,
    ObjectNotFoundError,
)
from .map import map_storage


__all__ = [
    "FileStorage",
    "DictStorage",
    "IStorage",
    "StorageTypeUnknownError",
    "StorageError",
    "ObjectNotFoundError",
    "map_storage",
]
