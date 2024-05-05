import pytest
from pathlib import Path
from src.storage import (
    FileStorage, StorageTypeUnknownError, ObjectNotFoundError, ObjectIsNotAFileError
)
from gcsfs import GCSFileSystem  # type: ignore
from fsspec.implementations.memory import MemoryFileSystem  # type: ignore
from fsspec.implementations.local import LocalFileSystem  # type: ignore


PATH = Path(__file__).parent.resolve()
int_ = 1


class TestFileStorage:

    datapath = "memory://storage"
    files = [
        #  filepath, filecontent, content_type
        ("first.txt", "content", "string"),
        ("second.bytes", int_.to_bytes(), "bytes"),
        ("/subfolder/third.txt", "new content", "string"),
    ]

    @pytest.fixture(scope="session")
    def setup(self):

        fs = MemoryFileSystem()
        fs.mkdir(self.datapath + "/subfolder/")

        for filepath, content, content_type in self.files:
            filepath = self.datapath + "/" + filepath
            if content_type == "bytes":
                fs.write_bytes(filepath, content)
            else:
                fs.write_text(filepath, content)

        yield

    @pytest.fixture
    def storage(self) -> FileStorage:
        return FileStorage()

    def test_correctly_setting_file_systems(self, storage: FileStorage):

        assert isinstance(storage.protocols["local://"], LocalFileSystem)
        assert isinstance(storage.protocols["gs://"], GCSFileSystem)

    def test_unknown_protocols_lead_to_errors(self, storage: FileStorage):
        # given a file storage
        storage = storage

        # when a path with unknown protocol is specified
        path = "https://any/path"

        # then trying to find, read or writy objects raises StorageTypeUnknownError
        with pytest.raises(StorageTypeUnknownError):
            storage.find(path=path)
        with pytest.raises(StorageTypeUnknownError):
            storage.read(path=path)
        with pytest.raises(StorageTypeUnknownError):
            storage.write(content=b"sdf", path=path)

    def test_reading_non_existing_files_raises_error(self, setup, storage: FileStorage):
        # given a FileStorage
        storage = storage

        # when a non-existing file is specifeid for reading
        filepath = self.datapath + "/doesntexist.txt"

        # then trying to read this file results in ObjectNotFoundError
        with pytest.raises(ObjectNotFoundError):
            _ = storage.read(path=filepath)

    def test_reading_folders_raises_error(self, setup, storage: FileStorage):
        # given a File Storage
        storage = storage

        # when a folder is specified as path to be read
        path = self.datapath + "/subfolder"

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
        assert self.datapath + "/first.txt" in found
        assert self.datapath + "/second.bytes" in found

    def test_that_text_files_are_read(self, setup, storage: FileStorage):

        # given an FileStorage
        storage = storage

        # when a an existing text file is read
        path = self.datapath + "/first.txt"
        content = storage.read(path=path)

        # then the file content assert that content is read correctly
        assert content == b"content"

    def test_that_byte_valued_files_are_read(self, setup, storage: FileStorage):

        # given a FileStorage
        storage = storage

        # when a an existing bytefile with is read
        path = self.datapath + "/second.bytes"
        content = storage.read(path=path)

        # then the file content is correctly read and returned as bytes
        assert int.from_bytes(content) == 1

    def test_writing_to_subfolders(self, setup, storage: FileStorage):

        # given a FileStorage
        storage = storage

        # when a non-existing file in a non-existing subfolder is specified
        filepath = self.datapath + "/ne/file.txt"
        content = b"any content"

        # then writing to this path succeeds
        storage.write(content=content, path=filepath)
        assert storage.read(filepath) == content
