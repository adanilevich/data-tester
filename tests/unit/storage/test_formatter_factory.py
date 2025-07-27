import pytest

from src.storage.formatter_factory import FormatterFactory
from src.storage.json_formatter import JsonFormatter
from src.dtos import StorageObject


class TestFormatterFactory:
    """Test FormatterFactory implementation"""

    @pytest.fixture
    def factory(self) -> FormatterFactory:
        return FormatterFactory()

    def test_get_formatter_returns_json_formatter(self, factory: FormatterFactory):
        """Test that get_formatter returns JsonFormatter for all supported object types"""
        supported_types = [
            StorageObject.DOMAIN_CONFIG,
            StorageObject.SPECIFICATION,
            StorageObject.TESTRUN,
            StorageObject.TESTCASE_REPORT,
            StorageObject.TESTRUN_REPORT,
            StorageObject.TESTSET,
        ]

        for object_type in supported_types:
            formatter = factory.get_formatter(object_type)
            assert isinstance(formatter, JsonFormatter)

    def test_get_formatter_same_instance(self, factory: FormatterFactory):
        """Test that get_formatter returns the same JsonFormatter instance"""
        formatter1 = factory.get_formatter(StorageObject.TESTSET)
        formatter2 = factory.get_formatter(StorageObject.DOMAIN_CONFIG)

        # Should return the same instance (singleton pattern)
        assert formatter1 is formatter2

    def test_get_formatter_unknown_object_type_raises(self, factory: FormatterFactory):
        """Test that unknown object types raise ValueError"""
        with pytest.raises(
            ValueError, match="Cannot get formatter for unknown object type"
        ):
            factory.get_formatter(StorageObject.UNKNOWN)

    def test_factory_creates_json_formatter_once(self, factory: FormatterFactory):
        """Test that the factory creates the JsonFormatter only once"""
        # Access the private attribute to verify singleton behavior
        assert hasattr(factory, "_json_formatter")

        formatter1 = factory.get_formatter(StorageObject.TESTSET)
        formatter2 = factory.get_formatter(StorageObject.TESTRUN)

        # Both should be the same instance and the same as the private attribute
        assert formatter1 is formatter2
        assert formatter1 is factory._json_formatter
