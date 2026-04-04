import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Type

from fsspec import AbstractFileSystem
from fsspec.implementations.local import LocalFileSystem
from fsspec.implementations.memory import MemoryFileSystem

try:
    from gcsfs import GCSFileSystem
except ImportError:
    GCSFileSystem = None  # ty: ignore[invalid-assignment]

from src.infrastructure_ports import (
    IDtoStorage,
    StorageError,
    ObjectNotFoundError,
)
from src.dtos import (
    DomainConfigDTO,
    SpecificationDTO,
    TestSetDTO,
    TestRunDTO,
    TestCaseReportDTO,
    TestRunReportDTO,
    LocationDTO,
    ObjectType,
    DTO
)


# --- Serializer interface and implementation ---


class SerializerError(Exception):
    """Base error for serializer operations."""


class DeserializationError(SerializerError):
    """Error during deserialization."""


class ISerializer(ABC):
    """Interface for serializing and deserializing DTO objects."""

    file_suffix: str

    @abstractmethod
    def serialize(self, dto: DTO) -> bytes:
        """Serialize a DTO object to bytes."""

    @abstractmethod
    def deserialize(self, data: bytes, object_type: ObjectType) -> DTO:
        """Deserialize bytes back to a DTO object."""


class JsonSerializer(ISerializer):
    """JSON serializer for DTO objects."""

    file_suffix: str = "json"

    def __init__(self) -> None:
        self._dto_mapping: Dict[ObjectType, Type[DTO]] = {
            ObjectType.DOMAIN_CONFIG: DomainConfigDTO,
            ObjectType.SPECIFICATION: SpecificationDTO,
            ObjectType.TESTRUN: TestRunDTO,
            ObjectType.TESTCASE_REPORT: TestCaseReportDTO,
            ObjectType.TESTRUN_REPORT: TestRunReportDTO,
            ObjectType.TESTSET: TestSetDTO,
        }

    def serialize(self, dto: DTO) -> bytes:
        return dto.to_json().encode("utf-8")

    def deserialize(self, data: bytes, object_type: ObjectType) -> DTO:
        if object_type not in self._dto_mapping:
            raise SerializerError(f"Unknown object type: {object_type}")

        dto_class = self._dto_mapping[object_type]
        try:
            json_data = json.loads(data.decode("utf-8"))
        except json.JSONDecodeError as err:
            raise DeserializationError(
                f"Error deserialzng JSON to {dto_class.__name__}: {data.decode('utf-8')}"
            ) from err
        try:
            result = dto_class.from_dict(json_data)
        except Exception as err:
            raise DeserializationError(
                f"Error deserialzng JSON to {dto_class.__name__}: {json_data}"
            ) from err

        return result


# --- Storage ---


class DtoStorageFileError(StorageError):
    """Error raised by file-based DTO storage implementations."""


# Mapping from DTO class to ObjectType
_DTO_TYPE_MAPPING: Dict[Type[DTO], ObjectType] = {
    DomainConfigDTO: ObjectType.DOMAIN_CONFIG,
    TestSetDTO: ObjectType.TESTSET,
    TestRunDTO: ObjectType.TESTRUN,
    TestCaseReportDTO: ObjectType.TESTCASE_REPORT,
    TestRunReportDTO: ObjectType.TESTRUN_REPORT,
}


def _infer_object_type(dto: DTO) -> ObjectType:
    """Infer ObjectType from the DTO's class."""
    for dto_class, object_type in _DTO_TYPE_MAPPING.items():
        if isinstance(dto, dto_class):
            return object_type
    raise DtoStorageFileError(f"Cannot infer ObjectType for DTO: {str(dto)}")


class DtoStorageFile(IDtoStorage):
    """
    File-based DTO storage using fsspec. Storage location is fixed at
    construction time. DTOs are organized in subfolders by type, domain,
    date, and testrun_id.
    """

    def __init__(
        self,
        serializer: ISerializer,
        storage_location: LocationDTO,
        fs: AbstractFileSystem,
    ):
        self.serializer: ISerializer = serializer
        self.storage_location: LocationDTO = storage_location
        self.fs: AbstractFileSystem = fs

    def _get_subfolder(self, dto: DTO, object_type: ObjectType) -> str:
        """Determine the subfolder path from DTO attributes."""
        match object_type:
            case ObjectType.DOMAIN_CONFIG:
                return "domain_configs/"
            case ObjectType.TESTSET:
                domain: str = getattr(dto, "domain", "")
                return f"testsets/{domain}/"
            case ObjectType.TESTRUN:
                domain = getattr(dto, "domain", "")
                start_ts: datetime = getattr(dto, "start_ts", datetime.now())
                date_str = start_ts.strftime("%Y-%m-%d")
                return f"testruns/{domain}/{date_str}/"
            case ObjectType.TESTRUN_REPORT:
                domain = getattr(dto, "domain", "")
                start_ts = getattr(dto, "start_ts", datetime.now())
                date_str = start_ts.strftime("%Y-%m-%d")
                return f"testrun_reports/{domain}/{date_str}/"
            case ObjectType.TESTCASE_REPORT:
                domain = getattr(dto, "domain", "")
                start_ts = getattr(dto, "start_ts", datetime.now())
                date_str = start_ts.strftime("%Y-%m-%d")
                testrun_id = str(getattr(dto, "testrun_id", ""))
                return f"testcase_reports/{domain}/{date_str}/{testrun_id}/"
            case _:
                raise DtoStorageFileError(f"Unknown object type: {object_type}")

    def _get_folder(self, object_type: ObjectType) -> str:
        """Returns the top-level type folder."""
        match object_type:
            case ObjectType.DOMAIN_CONFIG:
                return "domain_configs/"
            case ObjectType.TESTSET:
                return "testsets/"
            case ObjectType.TESTRUN:
                return "testruns/"
            case ObjectType.TESTRUN_REPORT:
                return "testrun_reports/"
            case ObjectType.TESTCASE_REPORT:
                return "testcase_reports/"
            case _:
                raise DtoStorageFileError(f"Unknown object type: {object_type}")

    def write_dto(self, dto: DTO) -> None:
        object_type = _infer_object_type(dto)
        subfolder = self._get_subfolder(dto, object_type)
        key = f"{object_type.value.lower()}_{dto.object_id}.{self.serializer.file_suffix}"
        full_path = self.storage_location.path + subfolder + key

        serialized = self.serializer.serialize(dto)
        try:
            with self.fs.open(full_path, mode="wb") as f:
                f.write(serialized)
        except Exception as err:
            raise DtoStorageFileError(f"Error writing DTO: {str(dto)}") from err

    def read_dto(self, object_type: ObjectType, id: str) -> DTO:
        object_key = f"{object_type.value.lower()}_{id}.{self.serializer.file_suffix}"
        base_folder = self.storage_location.path + self._get_folder(object_type)
        pattern = base_folder + "**/" + object_key

        try:
            matches = self.fs.glob(pattern)
        except Exception:
            matches = []

        if not matches:
            raise ObjectNotFoundError(f"Object {id} of type {object_type}")

        if len(matches) > 1:
            raise DtoStorageFileError(f"Multiple {object_type} found for {id}")

        try:
            with self.fs.open(matches[0], mode="rb") as f:
                content = f.read()
        except Exception as err:
            raise DtoStorageFileError(f"Error reading {object_type}: {id}") from err

        return self.serializer.deserialize(content, object_type)

    def list_dtos(
        self,
        object_type: ObjectType,
        filters: Dict[str, str] | None = None,
        order_by: str | None = None,
    ) -> List[DTO]:
        if order_by is not None and order_by != "date":
            raise ValueError(f"Unsupported order_by: {order_by}.Only 'date' supported.")

        search_path = self.storage_location.path + self._get_folder(object_type)

        # Apply filters to narrow the search path
        if filters:
            if "domain" in filters:
                search_path += f"{filters['domain']}/"
            if "date" in filters:
                search_path += f"{filters['date']}/"
            if "testrun_id" in filters:
                search_path += f"{filters['testrun_id']}/"

        # Build glob pattern for matching files
        glob_pattern = (
            search_path +
            f"**/{object_type.value.lower()}_*." +
            self.serializer.file_suffix
        )

        try:
            matches = self.fs.glob(glob_pattern)
        except Exception:
            matches = []

        results: List[DTO] = []
        for match_path in matches:
            try:
                with self.fs.open(match_path, mode="rb") as f:
                    content = f.read()
                dto = self.serializer.deserialize(content, object_type)
                results.append(dto)
            except Exception:
                continue

        if order_by == "date":
            results.sort(key=lambda d: getattr(d, "start_ts", datetime.min))

        return results


class MemoryDtoStorage(DtoStorageFile):
    def __init__(
        self,
        serializer: ISerializer,
        storage_location: LocationDTO,
    ) -> None:
        super().__init__(serializer, storage_location, MemoryFileSystem())


class LocalDtoStorage(DtoStorageFile):
    def __init__(
        self,
        serializer: ISerializer,
        storage_location: LocationDTO,
    ) -> None:
        super().__init__(serializer, storage_location, LocalFileSystem(auto_mkdir=True))


class GcsDtoStorage(DtoStorageFile):
    def __init__(
        self,
        serializer: ISerializer,
        storage_location: LocationDTO,
        gcp_project: str,
    ) -> None:
        if GCSFileSystem is None:
            raise ImportError("gcsfs is not installed. ")
        super().__init__(serializer, storage_location, GCSFileSystem(project=gcp_project))
