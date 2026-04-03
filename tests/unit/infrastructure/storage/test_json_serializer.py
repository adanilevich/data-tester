import pytest
import json

from src.infrastructure.storage.dto_storage_file import (
    JsonSerializer,
    SerializerError,
)
from src.dtos import TestSetDTO, ObjectType


class TestJsonSerializer:
    """Test JsonSerializer implementation"""

    @pytest.fixture
    def serializer(self) -> JsonSerializer:
        return JsonSerializer()

    @pytest.fixture
    def test_dto(self) -> TestSetDTO:
        return TestSetDTO(
            name="Test Testset",
            domain="test-domain",
            default_stage="dev",
            default_instance="test-instance",
            testcases={},
        )

    def test_roundtrip_serialization(
        self, serializer: JsonSerializer, test_dto: TestSetDTO
    ):
        """Test complete roundtrip: serialize -> deserialize -> should match original"""
        serialized = serializer.serialize(test_dto)

        assert isinstance(serialized, bytes)

        data = json.loads(serialized.decode("utf-8"))
        assert isinstance(data, dict)
        assert data["name"] == "Test Testset"
        assert data["domain"] == "test-domain"

        deserialized = serializer.deserialize(
            serialized, ObjectType.TESTSET
        )

        assert isinstance(deserialized, TestSetDTO)
        assert deserialized.name == test_dto.name
        assert deserialized.domain == test_dto.domain
        assert deserialized.default_stage == test_dto.default_stage
        assert deserialized.default_instance == test_dto.default_instance
        assert str(deserialized.testset_id) == str(
            test_dto.testset_id
        )

    def test_unknown_object_type_raises(
        self, serializer: JsonSerializer
    ):
        """Test that unknown object types raise SerializerError"""
        with pytest.raises(
            SerializerError, match="Unknown object type"
        ):
            serializer.deserialize(b"{}", ObjectType.UNKNOWN)

    def test_deserialize_invalid_json_raises(
        self, serializer: JsonSerializer
    ):
        """Test that invalid JSON raises DeserializationError"""
        from src.infrastructure.storage.dto_storage_file import (
            DeserializationError,
        )

        with pytest.raises(DeserializationError):
            serializer.deserialize(
                b"not-json", ObjectType.TESTSET
            )
