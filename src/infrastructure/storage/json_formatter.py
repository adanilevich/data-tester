import json
from typing import Dict, Type

from .i_formatter import IFormatter
from src.dtos.dto import DTO
from src.dtos.location import StorageObject
from src.dtos import (
    DomainConfigDTO,
    SpecificationDTO,
    TestRunDTO,
    TestCaseReportDTO,
    TestRunReportDTO,
    TestSetDTO,
)


class JsonFormatter(IFormatter):
    """JSON formatter for serializing and deserializing DTO objects."""

    def __init__(self):
        self._dto_mapping: Dict[StorageObject, Type[DTO]] = {
            StorageObject.DOMAIN_CONFIG: DomainConfigDTO,
            StorageObject.SPECIFICATION: SpecificationDTO,
            StorageObject.TESTRUN: TestRunDTO,
            StorageObject.TESTCASE_REPORT: TestCaseReportDTO,
            StorageObject.TESTRUN_REPORT: TestRunReportDTO,
            StorageObject.TESTSET: TestSetDTO,
        }

    def serialize(self, dto: DTO) -> bytes:
        """Serialize a DTO object to JSON bytes."""
        return dto.to_json().encode("utf-8")

    def deserialize(self, data: bytes, object_type: StorageObject) -> DTO:
        """Deserialize JSON bytes back to a DTO object."""
        if object_type not in self._dto_mapping:
            raise ValueError(f"Unknown object type: {object_type}")

        dto_class = self._dto_mapping[object_type]
        json_data = json.loads(data.decode("utf-8"))
        return dto_class.from_dict(json_data)

    def get_object_key(self, object_id: str, object_type: StorageObject) -> str:
        """Get the JSON filename for storing an object."""
        object_prefix = object_type.value.lower()
        return f"{object_prefix}_{object_id}.json"

    def check_filename(self, filename: str, object_type: StorageObject) -> bool:
        """Check if filename corresponds to naming convention for given object type."""
        object_prefix = object_type.value.lower()
        expected_pattern = f"{object_prefix}_"
        return filename.startswith(expected_pattern) and filename.endswith(".json")

    def get_object_id(self, object_key: str, object_type: StorageObject) -> str:
        """Extract object ID from object key based on naming convention."""
        if not self.check_filename(object_key, object_type):
            raise ValueError(
                f"Object key '{object_key}' does not match naming convention "
                f"for {object_type.value}"
            )

        object_prefix = object_type.value.lower()
        prefix_len = len(f"{object_prefix}_")
        suffix_len = len(".json")

        return object_key[prefix_len:-suffix_len]
