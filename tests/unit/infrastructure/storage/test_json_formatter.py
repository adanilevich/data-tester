import pytest
import json

from src.infrastructure.storage.json_formatter import JsonFormatter
from src.infrastructure.storage.i_formatter import FormatterError
from src.dtos import TestSetDTO, StorageObject


class TestJsonFormatter:
    """Test JsonFormatter implementation"""

    @pytest.fixture
    def formatter(self) -> JsonFormatter:
        return JsonFormatter()

    @pytest.fixture
    def test_dto(self) -> TestSetDTO:
        return TestSetDTO(
            name="Test Testset",
            domain="test-domain",
            default_stage="dev",
            default_instance="test-instance",
            testcases={},
        )

    def test_get_object_key(self, formatter: JsonFormatter):
        """Test generating object keys for storage"""
        object_id = "test-id-123"
        object_type = StorageObject.TESTSET

        result = formatter.get_object_key(object_id, object_type)

        # Should follow the naming convention: {object_type}_{object_id}.json
        expected = "testset_test-id-123.json"
        assert result == expected

    def test_check_filename_valid(self, formatter: JsonFormatter):
        """Test checking valid filenames"""
        valid_filenames = [
            "testset_abc123.json",
            "domain_config_test.json",
            "testrun_report_xyz.json",
        ]

        for filename in valid_filenames:
            object_type = StorageObject.TESTSET  # Use consistent type for test
            if "domain_config" in filename:
                object_type = StorageObject.DOMAIN_CONFIG
            elif "testrun_report" in filename:
                object_type = StorageObject.TESTRUN_REPORT

            result = formatter.check_filename(filename, object_type)
            assert result is True

    def test_check_filename_invalid(self, formatter: JsonFormatter):
        """Test checking invalid filenames"""
        invalid_cases = [
            ("testset_abc123.txt", StorageObject.TESTSET),  # Wrong extension
            ("wrongtype_abc123.json", StorageObject.TESTSET),  # Wrong prefix
            ("testset.json", StorageObject.TESTSET),  # Missing ID
            ("abc123.json", StorageObject.TESTSET),  # Missing prefix
        ]

        for filename, object_type in invalid_cases:
            result = formatter.check_filename(filename, object_type)
            assert result is False

    def test_get_object_id_valid(self, formatter: JsonFormatter):
        """Test extracting object ID from valid object keys"""
        test_cases = [
            ("testset_abc123.json", StorageObject.TESTSET, "abc123"),
            ("domain_config_my-domain.json", StorageObject.DOMAIN_CONFIG, "my-domain"),
            ("testrun_report_uuid-here.json", StorageObject.TESTRUN_REPORT, "uuid-here"),
        ]

        for object_key, object_type, expected_id in test_cases:
            result = formatter.get_object_id(object_key, object_type)
            assert result == expected_id

    def test_get_object_id_invalid(self, formatter: JsonFormatter):
        """Test extracting object ID from invalid object keys raises ValueError"""
        invalid_cases = [
            ("testset_abc123.txt", StorageObject.TESTSET),  # Wrong extension
            ("wrongtype_abc123.json", StorageObject.TESTSET),  # Wrong prefix
            ("invalid.json", StorageObject.TESTSET),  # No matching pattern
        ]

        for object_key, object_type in invalid_cases:
            with pytest.raises(FormatterError):
                formatter.get_object_id(object_key, object_type)

    def test_roundtrip_serialization(
        self, formatter: JsonFormatter, test_dto: TestSetDTO
    ):
        """Test complete roundtrip: serialize -> deserialize -> should match original"""
        # Serialize
        serialized = formatter.serialize(test_dto)

        assert isinstance(serialized, bytes)

        # Should be valid JSON
        data = json.loads(serialized.decode("utf-8"))
        assert isinstance(data, dict)
        assert data["name"] == "Test Testset"
        assert data["domain"] == "test-domain"

        # Deserialize
        deserialized = formatter.deserialize(serialized, StorageObject.TESTSET)

        # Should match original
        assert isinstance(deserialized, TestSetDTO)
        assert deserialized.name == test_dto.name
        assert deserialized.domain == test_dto.domain
        assert deserialized.default_stage == test_dto.default_stage
        assert deserialized.default_instance == test_dto.default_instance
        assert str(deserialized.testset_id) == str(test_dto.testset_id)

    def test_unknown_object_type_raises(self, formatter: JsonFormatter):
        """Test that unknown object types raise ValueError"""
        with pytest.raises(FormatterError, match="Unknown object type"):
            formatter.deserialize(b"{}", StorageObject.UNKNOWN)
