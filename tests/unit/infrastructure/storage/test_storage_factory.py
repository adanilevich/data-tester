import pytest

from src.infrastructure.storage.storage_factory import StorageFactory
from src.infrastructure.storage.formatter_factory import FormatterFactory
from src.infrastructure.storage.file_storage import FileStorage
from src.infrastructure.storage.dict_storage import DictStorage
from src.dtos import LocationDTO, Store


class TestStorageFactory:
    """Test StorageFactory implementation"""

    @pytest.fixture
    def formatter_factory(self) -> FormatterFactory:
        return FormatterFactory()

    @pytest.fixture
    def storage_factory(self, formatter_factory: FormatterFactory) -> StorageFactory:
        return StorageFactory(formatter_factory)

    def test_get_storage(self, storage_factory: StorageFactory):
        """Test getting different storage types"""
        # Test local file storage
        local_location = LocationDTO("local://test/path")
        local_storage = storage_factory.get_storage(local_location)
        assert isinstance(local_storage, FileStorage)
        assert local_storage.storage_type == Store.LOCAL

        # Test memory file storage
        memory_location = LocationDTO("memory://test/path")
        memory_storage = storage_factory.get_storage(memory_location)
        assert isinstance(memory_storage, FileStorage)
        assert memory_storage.storage_type == Store.MEMORY

        # Test dict storage
        dict_location = LocationDTO("dict://test/path")
        dict_storage = storage_factory.get_storage(dict_location)
        assert isinstance(dict_storage, DictStorage)

        # Verify different types return different instances
        assert local_storage is not dict_storage
        assert memory_storage is not dict_storage

    def test_get_storage_passes_formatter_factory(self, storage_factory: StorageFactory):
        """Test that the formatter factory is passed to storage instances"""
        location = LocationDTO("dict://test/path")

        storage = storage_factory.get_storage(location)

        # DictStorage should have the formatter factory
        assert hasattr(storage, "formatter_factory")
        assert storage.formatter_factory is storage_factory.formatter_factory

    def test_get_storage_passes_config_to_file_storage(
        self, storage_factory: StorageFactory
    ):
        """Test that config is passed to FileStorage instances"""
        location = LocationDTO("local://test/path")

        storage = storage_factory.get_storage(location)

        # FileStorage should have the config
        assert hasattr(storage, "gcp_project")
        assert storage.gcp_project is None

    def test_unsupported_storage_type_raises(self, storage_factory: StorageFactory):
        """Test that unsupported storage types raise ValueError"""
        # The error comes from Store enum validation when accessing .store property
        location = LocationDTO("unsupported://test/path")
        with pytest.raises(ValueError, match="is not a valid Store"):
            storage_factory.get_storage(location)
