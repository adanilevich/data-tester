"""
Ports module containing interface definitions for the hexagonal architecture.

This module defines the contracts between the domain/application layers and the
infrastructure layer, ensuring proper dependency inversion.
"""

from .i_backend import IBackend, BackendError
from .i_backend_factory import IBackendFactory
from .i_storage import (
    IStorage,
    StorageError,
    StorageTypeUnknownError,
    ObjectNotFoundError,
)
from .i_storage_factory import IStorageFactory
from .i_notifier import INotifier

__all__ = [
    "IBackend",
    "IBackendFactory",
    "BackendError",
    "IStorage",
    "IStorageFactory",
    "StorageError",
    "StorageTypeUnknownError",
    "ObjectNotFoundError",
    "INotifier",
]
