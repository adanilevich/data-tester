class StorageError(Exception):
    """Base exception for storage operations."""


class StorageTypeUnknownError(StorageError):
    """
    Exception raised when a storage type is not supported.
    """

    def __init__(self, message: str = "Storage type not supported"):
        super().__init__(message)


class ObjectNotFoundError(StorageError):
    """
    Exception raised when an object is not found in storage.
    """

    def __init__(self, message: str = "Object not found"):
        super().__init__(message)
