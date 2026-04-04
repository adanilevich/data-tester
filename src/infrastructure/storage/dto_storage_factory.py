from src.dtos.storage_dtos import LocationDTO, StorageType
from src.infrastructure_ports import (
    IDtoStorageFactory,
    IDtoStorage,
    StorageTypeUnknownError,
)
from .dto_storage_file import (
    MemoryDtoStorage,
    LocalDtoStorage,
    GcsDtoStorage,
    JsonSerializer,
)


class DtoStorageFactory(IDtoStorageFactory):
    """Factory for creating DTO storage instances based on storage location."""

    def __init__(self, gcp_project: str | None = None):
        self._gcp_project: str | None = gcp_project
        self._serializer = JsonSerializer()

    def get_storage(self, storage_location: LocationDTO) -> IDtoStorage:
        match storage_location.storage_type:
            case StorageType.MEMORY:
                return MemoryDtoStorage(
                    serializer=self._serializer,
                    storage_location=storage_location,
                )
            case StorageType.LOCAL:
                return LocalDtoStorage(
                    serializer=self._serializer,
                    storage_location=storage_location,
                )
            case StorageType.GCS:
                if self._gcp_project is None:
                    raise StorageTypeUnknownError(
                        "GCS storage requires gcp_project configuration"
                    )
                return GcsDtoStorage(
                    serializer=self._serializer,
                    storage_location=storage_location,
                    gcp_project=self._gcp_project,
                )
            case _:
                raise StorageTypeUnknownError(
                    f"Storage type {storage_location.storage_type} not supported"
                )
