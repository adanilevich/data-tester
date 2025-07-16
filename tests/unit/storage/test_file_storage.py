import pytest
from pathlib import Path
from src.storage import (
    FileStorage, StorageTypeUnknownError, ObjectNotFoundError, ObjectIsNotAFileError,
    FileStorageError
)
from fsspec.implementations.memory import MemoryFileSystem  # type: ignore
from fsspec.implementations.local import LocalFileSystem  # type: ignore
from fsspec.spec import AbstractFileSystem  # type: ignore
from src.dtos.location import LocationDTO, Store
from unittest import mock


PATH = Path(__file__).parent.resolve()
int_ = 1


# TODO: increase test coverage
class TestFileStorage:

    files = [
        #  filepath, filecontent, content_type
        ("first.txt", "content", "string"),
        ("second.bytes", int_.to_bytes(), "bytes"),
        ("subfolder/third.txt", "new content", "string"),
    ]

    @property
    def datapath(self) -> LocationDTO:
        return LocationDTO("memory://storage")

    @pytest.fixture
    def setup(self):

        fs = MemoryFileSystem()
        fs.mkdir(self.datapath.path + "subfolder/")

        for filepath, content, content_type in self.files:
            filepath = self.datapath.path + filepath
            if content_type == "bytes":
                fs.write_bytes(filepath, content)
            else:
                fs.write_text(filepath, content)

        yield

        fs.rm(self.datapath.path, recursive=True)

    @pytest.fixture
    def storage(self) -> FileStorage:
        return FileStorage()

    def test_setting_file_systems(self, storage: FileStorage, setup):

        assert isinstance(storage.protocols[Store.LOCAL], LocalFileSystem)
        assert isinstance(storage.protocols[Store.MEMORY], MemoryFileSystem)

    def test_adding_unknown_protocols(self, storage: FileStorage):
        # given a file storage
        storage = storage

        # when a path with unknown protocol is specified
        path = LocationDTO("dict://any/path")

        # then trying to find, read or writy objects raises StorageTypeUnknownError
        with pytest.raises(StorageTypeUnknownError):
            storage.find(path=path)
        with pytest.raises(StorageTypeUnknownError):
            storage.read(path=path)
        with pytest.raises(StorageTypeUnknownError):
            storage.write(content=b"sdf", path=path)

    def test_reading_non_existing_files(self, setup, storage: FileStorage):
        # given a FileStorage
        storage = storage

        # when a non-existing file is specifeid for reading
        filepath = self.datapath.append("doesntexist.txt")

        # then trying to read this file results in ObjectNotFoundError
        with pytest.raises(ObjectNotFoundError):
            _ = storage.read(path=filepath)

    def test_reading_folders(self, setup, storage: FileStorage):
        # given a File Storage
        storage = storage

        # when a folder is specified as path to be read
        path = self.datapath.append("subfolder")

        # then trying to read from this path raises ObjectIsNotAFileError
        with pytest.raises(ObjectIsNotAFileError):
            _ = storage.read(path=path)

    def test_only_top_level_files_are_found(self, setup, storage: FileStorage):
        # given a FileStorage
        storage = storage

        # when a top-level path which contains subfolders is specified
        path = self.datapath

        # only top-level objects are returned when searching in this path
        found = storage.find(path=path)
        assert len(found) == 2
        path1 = self.datapath.append("first.txt")
        path2 = self.datapath.append("second.bytes")
        assert path1 in found
        assert path2 in found

    def test_reading_text_files(self, setup, storage: FileStorage):

        # given an FileStorage
        storage = storage

        # when a an existing text file is read
        path = self.datapath.append("first.txt")
        content = storage.read(path=path)

        # then the file content assert that content is read correctly
        assert content == b"content"

    def test_reading_byte_valued_files(self, setup, storage: FileStorage):

        # given a FileStorage
        storage = storage

        # when a an existing bytefile with is read
        path = self.datapath.append("second.bytes")
        content = storage.read(path=path)

        # then the file content is correctly read and returned as bytes
        assert int.from_bytes(content) == 1

    def test_writing_to_subfolders(self, setup, storage: FileStorage):

        # given a FileStorage
        storage = storage

        # when a non-existing file in a non-existing subfolder is specified
        filepath = self.datapath.append("ne/file.txt")
        content = b"any content"

        # then writing to this path succeeds
        storage.write(content=content, path=filepath)
        assert storage.read(path=filepath) == content

    def test_double_write_read_roundtrip(self, setup, storage: FileStorage):
        # given a FileStorage
        storage = storage

        # when two files are written to the same path
        filepath = self.datapath.append("file1.txt")
        content1 = b"any content"
        storage.write(content=content1, path=filepath)
        content2 = b"any other content"
        storage.write(content=content2, path=filepath)

        # and when a third file is written to another path
        filepath2 = self.datapath.append("file2.txt")
        content3 = b"any other content"
        storage.write(content=content3, path=filepath2)

        # then the files are read correctly
        assert storage.read(path=filepath) == content2
        assert storage.read(path=filepath2) == content3

    def test_find(self, setup, storage: FileStorage):
        # given a FileStorage
        storage = storage

        # when a path is specified which contains two files
        path = self.datapath

        # then only top-level files are found
        found = storage.find(path=path)
        assert len(found) == 2
        assert self.datapath.append("first.txt") in found
        assert self.datapath.append("second.bytes") in found

        # when a path is specified which contains a subfolder
        path = self.datapath.append("subfolder")

        # then the files are found and the correct paths are returned
        found = storage.find(path=path)
        assert found == [self.datapath.append("subfolder/third.txt")]

    def test__protocol_local(self, storage: FileStorage):
        # given a FileStorage and LocalFileSystem
        fs = storage.protocols[Store.LOCAL]
        # when calling _protocol with LocalFileSystem
        result = storage._protocol(fs)
        # then it should return Store.LOCAL
        assert result == Store.LOCAL

    def test__protocol_storage_type_not_supported(self, storage: FileStorage):
        # given a FileStorage and an unknown AbstractFileSystem
        fs = AbstractFileSystem()
        # when calling _protocol with an unsupported fs
        # then it should raise StorageTypeUnknownError
        with pytest.raises(StorageTypeUnknownError):
            storage._protocol(fs)

    def test_find_no_object_found(self, storage: FileStorage):
        # given a FileStorage and a non-existing directory path
        path = LocationDTO("memory://non_existing_dir/")
        # when calling find on a non-existing directory
        # then it should raise ObjectNotFoundError
        with pytest.raises(ObjectNotFoundError):
            storage.find(path)

    def test_find_object_isfile_raises(self, storage: FileStorage):
        # given a FileStorage and a directory with a file
        fs = storage.protocols[Store.MEMORY]
        fs.mkdir("file_exists_dir/")
        fs.write_text("file_exists_dir/file1.txt", "abc")
        path = LocationDTO("memory://file_exists_dir/file1.txt")
        # when calling find on the file path
        result = storage.find(path)
        # then it should return the file path in a list
        assert result == [path]

    def test__exists_raises_file_storage_error(self, storage: FileStorage):
        # given a FileStorage and a path
        path = LocationDTO("memory://storage/doesnotmatter.txt")
        fs = storage.protocols[Store.MEMORY]
        # when fs.exists raises an exception
        with mock.patch.object(fs, 'exists', side_effect=Exception("fail")):
            # then _exists should raise FileStorageError
            with pytest.raises(FileStorageError):
                storage._exists(path)

    def test_read_or_write_exception(self, storage: FileStorage):
        # given a FileStorage and a file path
        fs = storage.protocols[Store.MEMORY]
        fs.write_text("fail.txt", "abc")
        path = LocationDTO("memory://fail.txt")
        # when fs.open raises an exception during read
        with mock.patch.object(fs, 'open', side_effect=Exception("fail open")):
            # then read should raise FileStorageError
            with pytest.raises(FileStorageError):
                storage.read(path)
            # then write should also raise FileStorageError
            with pytest.raises(FileStorageError):
                storage.write(b"abc", path)

    def test_supported_storage_types(self, storage: FileStorage):
        # given a FileStorage
        types = storage.supported_storage_types
        # when checking supported_storage_types
        # then LOCAL and MEMORY should be present
        assert Store.LOCAL in types
        assert Store.MEMORY in types
