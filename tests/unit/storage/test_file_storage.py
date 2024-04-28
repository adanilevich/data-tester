import pytest
from pathlib import Path
from src.storage import FileStorageError, FileStorage
from gcsfs import GCSFileSystem  # type: ignore
from fsspec.implementations.memory import MemoryFileSystem  # type: ignore
from fsspec.implementations.local import LocalFileSystem  # type: ignore


PATH = Path(__file__).parent.resolve()
int_ = 1


class TestFileStorage:

    datapath = "memory://data"
    fs = MemoryFileSystem()
    storage = FileStorage()
    files = [
        ("first.txt", "content", "string"),
        ("second.bytes", int_.to_bytes(), "bytes"),
        ("/subfolder/third.txt", "new content", "string"),
    ]

    @pytest.fixture(scope="session")
    def setup(self):

        self.fs.mkdir(self.datapath + "/subfolder/")

        for filepath, content, content_type in self.files:
            filepath = self.datapath + "/" + filepath
            if content_type == "bytes":
                self.fs.write_bytes(filepath, content)
            else:
                self.fs.write_text(filepath, content)

        yield

    def test_correctly_setting_file_systems(self):

        assert isinstance(self.storage.protocols["local://"], LocalFileSystem)
        assert isinstance(self.storage.protocols["gs://"], GCSFileSystem)

    @pytest.mark.parametrize("protocol,error", (
        ("local://", False),
        ("http://", True)
    ))
    def test_unknown_protocols_lead_to_errors(self, protocol, error):
        if error:
            with pytest.raises(FileStorageError):
                _ = self.storage._fs(protocol)
        else:
            assert isinstance(self.storage._fs(protocol), LocalFileSystem | GCSFileSystem)

    @pytest.mark.parametrize("prefix,is_valid", (
        ("local://", True),
        ("gs://", True),
        ("s3://", False)
    ))
    def test_only_valid_prefixes_are_valid(self, prefix, is_valid):
        assert self.storage._protocol_is_valid(prefix) is is_valid

    def test_correct_prefix_is_returned_for_known_fs(self):
        assert isinstance(self.storage._fs("local://"), LocalFileSystem)
        assert isinstance(self.storage._fs("gs://"), GCSFileSystem)
        with pytest.raises(FileStorageError):
            self.storage._fs("sadf")

    def test_only_top_level_files_are_found(self, setup):

        found = self.storage.find(self.datapath)
        assert len(found) == 2
        assert self.datapath + "/first.txt" in found
        assert self.datapath + "/second.bytes" in found

    def test_that_text_files_are_read(self, setup):

        # given an initalized FileStorage
        storage = self.storage

        # when a an existing text file with default encoding is accessed
        path = self.datapath + "/first.txt"
        content_type = "plain/text"
        content = storage.read(path=path, content_type=content_type)

        # then the file content assert that content is read correctly
        assert content == "content"

    def test_that_byte_valued_files_are_read(self, setup):

        # given an initalized FileStorage
        storage = self.storage

        # when a an existing byte-encoded (text) file with default encoding is accessed
        path = self.datapath + "/second.bytes"
        content_type = "application/octet-stream"
        content = storage.read(path=path, content_type=content_type)

        # then the file content is correctly read and returned as bytes
        assert int.from_bytes(content) == 1
