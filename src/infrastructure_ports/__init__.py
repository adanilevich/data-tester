"""
Ports module containing interface definitions for the hexagonal architecture.

This module defines the contracts between the domain/application layers and the
infrastructure layer, ensuring proper dependency inversion.
"""

from .backend import IBackend, IBackendFactory, BackendError
from .storage import (
    IStorage,
    IStorageFactory,
    StorageError,
    StorageTypeUnknownError,
    ObjectNotFoundError,
)
from .notifier import INotifier

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
