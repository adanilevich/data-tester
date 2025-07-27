import pytest

from src.storage.dict_storage import (
    DictStorage,
    StorageTypeUnknownError,
    ObjectNotFoundError,
)
from src.storage.formatter_factory import FormatterFactory
from src.dtos import LocationDTO, Store, StorageObject, TestSetDTO


class TestDictStorage:
    """Test DictStorage implementation with new interface"""

    @pytest.fixture
    def storage(self) -> DictStorage:
        formatter_factory = FormatterFactory()
        return DictStorage(formatter_factory=formatter_factory)

    def test_supported_storage_types(self, storage: DictStorage):
        """Test that DictStorage reports correct supported storage types"""
        supported_types = storage.supported_storage_types
        assert Store.DICT in supported_types
        assert len(supported_types) == 1

    def test_write_read_dto_roundtrip(self, storage: DictStorage):
        """Test writing and reading a DTO object"""
        # given a test DTO (let it generate its own UUID)
        test_dto = TestSetDTO(
            name="Test Testset",
            domain="test-domain",
            default_stage="dev",
            default_instance="test-instance",
            testcases={}
        )
        test_id = test_dto.testset_id
        location = LocationDTO("dict://test")

        # when writing and reading the DTO
        storage.write(dto=test_dto, object_type=StorageObject.TESTSET, location=location)
        result = storage.read(
            object_type=StorageObject.TESTSET,
            object_id=str(test_id),
            location=location
        )

        # then the result should match the original
        assert isinstance(result, TestSetDTO)
        assert str(result.testset_id) == str(test_id)
        assert result.domain == "test-domain"
        assert result.name == "Test Testset"

    def test_read_nonexistent_object(self, storage: DictStorage):
        """Test reading a non-existent object raises ObjectNotFoundError"""
        location = LocationDTO("dict://test")

        with pytest.raises(ObjectNotFoundError):
            storage.read(
                object_type=StorageObject.TESTSET,
                object_id="nonexistent",
                location=location
            )

    def test_write_read_bytes_roundtrip(self, storage: DictStorage):
        """Test writing and reading raw bytes"""
        content = b"test content"
        location = LocationDTO("dict://test/file.txt")

        # when writing and reading bytes
        storage.write_bytes(content=content, location=location)
        result = storage.read_bytes(location=location)

        # then the content should match
        assert result == content

    def test_list_objects(self, storage: DictStorage):
        """Test listing objects of a specific type excludes subfolders"""
        location = LocationDTO("dict://testlist")
        subfolder_location = LocationDTO("dict://testlist/subfolder")

        # write multiple test objects in main folder
        test_ids = []
        for i in range(3):
            test_dto = TestSetDTO(
                name=f"Test Testset {i}",
                domain="test-domain",
                default_stage="dev",
                default_instance="test-instance",
                testcases={}
            )
            test_ids.append(str(test_dto.testset_id))
            storage.write(
                dto=test_dto, object_type=StorageObject.TESTSET, location=location
            )

        # write an object in subfolder that should NOT be listed
        subfolder_dto = TestSetDTO(
            name="Subfolder Testset",
            domain="test-domain",
            default_stage="dev",
            default_instance="test-instance",
            testcases={}
        )
        storage.write(
            dto=subfolder_dto,
            object_type=StorageObject.TESTSET,
            location=subfolder_location
        )

        # when listing objects
        objects = storage.list(location=location, object_type=StorageObject.TESTSET)

        # then we should get back only the top-level objects, not the subfolder one
        assert len(objects) == 3  # Should NOT include the subfolder object
        # ObjectLocationDTO should have located_object_id as a field
        for obj in objects:
            # obj should be ObjectLocationDTO with located_object_id field
            assert hasattr(obj, 'located_object_id')
            assert obj.located_object_id in test_ids
            # Ensure the subfolder object is not included
            assert obj.located_object_id != str(subfolder_dto.testset_id)

    def test_list_files(self, storage: DictStorage):
        """Test listing files using list_files method excludes subfolders"""
        location = LocationDTO("dict://testfiles")
        subfolder_location = LocationDTO("dict://testfiles/subfolder")

        # write some files in main folder
        storage.write_bytes(b"content1", location.append("file1.txt"))
        storage.write_bytes(b"content2", location.append("file2.txt"))

        # write a file in subfolder that should NOT be listed
        storage.write_bytes(
            b"subfolder content", subfolder_location.append("subfile.txt")
        )

        # when listing files
        files = storage.list_files(location=location)

        # then we should get back only top-level file locations, not subfolder files
        assert len(files) == 2  # Should NOT include the subfolder file
        filenames = [f.path.split("/")[-1] for f in files]
        assert "file1.txt" in filenames
        assert "file2.txt" in filenames
        # Ensure subfolder file is not included - only top-level files
        assert "subfile.txt" not in filenames

    def test_wrong_store_type_raises(self, storage: DictStorage):
        """Test that wrong storage types raise appropriate errors"""
        location = LocationDTO("local://folder/file.txt")
        test_dto = TestSetDTO(
            name="Test",
            domain="test",
            default_stage="dev",
            default_instance="test",
            testcases={}
        )

        with pytest.raises(StorageTypeUnknownError):
            storage.write(
                dto=test_dto, object_type=StorageObject.TESTSET, location=location
            )
        with pytest.raises(StorageTypeUnknownError):
            storage.read(
                object_type=StorageObject.TESTSET, object_id="test", location=location
            )
        with pytest.raises(StorageTypeUnknownError):
            storage.list(location=location, object_type=StorageObject.TESTSET)
