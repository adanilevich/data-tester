"""
Ports module containing interface definitions for the
hexagonal architecture.
"""

from .i_backend import IBackend, BackendError
from .i_backend_factory import IBackendFactory
from .errors import (
    StorageError,
    StorageTypeUnknownError,
    ObjectNotFoundError,
)
from .i_user_storage import IUserStorage
from .i_user_storage_factory import IUserStorageFactory
from .i_dto_storage import IDtoStorage
from .i_dto_storage_factory import IDtoStorageFactory
from .i_notifier import INotifier

__all__ = [
    "IBackend",
    "IBackendFactory",
    "BackendError",
    "IUserStorage",
    "IUserStorageFactory",
    "IDtoStorage",
    "IDtoStorageFactory",
    "StorageError",
    "StorageTypeUnknownError",
    "ObjectNotFoundError",
    "INotifier",
]
