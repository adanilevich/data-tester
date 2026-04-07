"""
Ports module containing interface definitions for the
hexagonal architecture.
"""

from .errors import (
    ObjectNotFoundError,
    StorageError,
    StorageTypeUnknownError,
)
from .i_backend import BackendError, IBackend
from .i_backend_factory import IBackendFactory
from .i_dto_storage import IDtoStorage
from .i_dto_storage_factory import IDtoStorageFactory
from .i_notifier import INotifier
from .i_user_storage import IUserStorage
from .i_user_storage_factory import IUserStorageFactory

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
